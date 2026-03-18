import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from devprod_api.config import Settings, get_settings
from devprod_api.exceptions import DevProdError
from devprod_api.knowledge import KnowledgeRepository
from devprod_api.models import (
    ErrorEnvelope,
    ErrorDetail,
    IncidentDetail,
    IncidentListResponse,
    InvestigationRunListResponse,
    InvestigationResult,
    ReadinessResponse,
    RunInvestigationRequest,
    RuntimeConfigResponse,
)
from devprod_api.providers import build_workflow_provider
from devprod_api.repository import IncidentRepository
from devprod_api.run_history import InvestigationRunStore
from devprod_api.security import enforce_request_controls
from devprod_api.workflow import WorkflowService


logger = logging.getLogger("devprod.api")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    app.state.settings = settings
    app.state.incidents = IncidentRepository()
    app.state.knowledge = KnowledgeRepository()
    app.state.run_store = InvestigationRunStore(settings.devprod_run_history_db_path)
    app.state.provider = build_workflow_provider(settings, app.state.knowledge)
    app.state.workflow = WorkflowService(
        settings=settings,
        incident_repository=app.state.incidents,
        provider=app.state.provider,
        run_store=app.state.run_store,
    )
    yield


app = FastAPI(title="DevProd API", version="0.1.0", lifespan=lifespan)


def get_runtime_settings() -> Settings:
    return get_settings()


def guard_request(
    request: Request,
    settings: Settings = Depends(get_runtime_settings),
    x_api_key: str | None = Header(default=None),
) -> None:
    enforce_request_controls(request, settings, x_api_key)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().devprod_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(DevProdError)
async def handle_domain_error(_: Request, exc: DevProdError) -> JSONResponse:
    payload = ErrorEnvelope(error=ErrorDetail(code=exc.code, message=exc.message))
    headers = {"Retry-After": "60"} if exc.status_code == 429 else {}
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump(), headers=headers)


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
    payload = ErrorEnvelope(error=ErrorDetail(code="internal_error", message="An internal error occurred."))
    return JSONResponse(status_code=500, content=payload.model_dump())


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readiness", response_model=ReadinessResponse)
async def readiness(request: Request) -> ReadinessResponse:
    workflow: WorkflowService = request.app.state.workflow
    return workflow.readiness()


@app.get("/v1/config", response_model=RuntimeConfigResponse, dependencies=[Depends(guard_request)])
async def runtime_config(settings: Settings = Depends(get_runtime_settings)) -> RuntimeConfigResponse:
    return RuntimeConfigResponse(
        demoMode=settings.demo_mode,
        authEnabled=settings.devprod_enable_auth,
        rateLimitPerMinute=settings.devprod_rate_limit_per_minute,
        providerMode="demo" if settings.demo_mode else "live",
    )


@app.get("/v1/incidents", response_model=IncidentListResponse, dependencies=[Depends(guard_request)])
async def list_incidents(request: Request) -> IncidentListResponse:
    repository: IncidentRepository = request.app.state.incidents
    return IncidentListResponse(incidents=repository.list_incidents())


@app.get(
    "/v1/incidents/{incident_id}",
    response_model=IncidentDetail,
    dependencies=[Depends(guard_request)],
)
async def get_incident(incident_id: str, request: Request) -> IncidentDetail:
    repository: IncidentRepository = request.app.state.incidents
    return repository.get_incident(incident_id)


@app.post(
    "/v1/investigations",
    response_model=InvestigationResult,
    dependencies=[Depends(guard_request)],
)
async def run_investigation(
    payload: RunInvestigationRequest,
    request: Request,
) -> InvestigationResult:
    workflow: WorkflowService = request.app.state.workflow
    return workflow.run(payload.incidentId)


@app.get(
    "/v1/investigations/runs",
    response_model=InvestigationRunListResponse,
    dependencies=[Depends(guard_request)],
)
async def list_recent_runs(request: Request) -> InvestigationRunListResponse:
    workflow: WorkflowService = request.app.state.workflow
    return InvestigationRunListResponse(runs=workflow.list_recent_runs())

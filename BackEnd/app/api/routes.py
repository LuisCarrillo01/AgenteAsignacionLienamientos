import asyncio

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.graph.workflow import build_workflow
from app.models.schemas import ClassificationRequest, ClassificationResponse


router = Blueprint("classification", __name__)
workflow = build_workflow()


@router.get("/health")
def healthcheck():
    return jsonify({"status": "ok"})


@router.post("/clasificar")
def clasificar():
    payload_json = request.get_json(silent=True)
    if payload_json is None:
        return jsonify({"error": "El cuerpo de la solicitud debe ser JSON valido."}), 400

    try:
        payload = ClassificationRequest.model_validate(payload_json)
    except ValidationError as exc:
        return jsonify({"error": "Solicitud invalida.", "details": exc.errors()}), 422

    result = asyncio.run(workflow.ainvoke({"payload": payload}))
    response = ClassificationResponse.model_validate(result["result"])
    return jsonify(response.model_dump())

from flask import Blueprint, request, jsonify
from middleware.jwt_middleware import token_required
from services.payment_service import premium_membership_service

payment_bp = Blueprint("payment_bp", __name__)

@payment_bp.route("/premium", methods=["POST"])
@token_required
def purchase_premium():
    """
    Purchase a premium membership.
    ---
    tags:
      - Payment
    summary: Purchase premium membership
    consumes:
      - application/json
    parameters:
      - in: body
        name: payment
        schema:
          type: object
          properties:
            plan:
              type: string
          required:
            - plan
    responses:
      200:
        description: Premium purchase processed successfully
    """
    response, status = premium_membership_service(request.user_id, request.json or {})
    return jsonify(response), status

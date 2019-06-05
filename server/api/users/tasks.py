from flask_restful import Resource, current_app, request
from dateutil.parser import parse as date_parse

from server.services.users.authentication_service import token_auth, tm
from server.services.users.user_service import UserService, NotFound


class UsersTasksAPI(Resource):
    @token_auth.login_required
    def get(self):
        """
        Gets tasks users has interacted
        ---
        tags:
          - user
        produces:
          - application/json
        parameters:
            - in: header
              name: Authorization
              description: Base64 encoded session token
              required: true
              type: string
              default: Token sessionTokenHere==
            - in: query
              name: taskStatus
              description: Task Status filter
              required: false
              type: string
              default: null
            - in: query
              name: project_id
              description: Project id
              required: false
              type: integer
              default: null
            - in: query
              name: start_date
              description: Date to filter as minimum
              required: false
              type: string
              default: null
            - in: query
              name: end_date
              description: Date to filter as maximum
              required: false
              type: string
              default: null
            - in: query
              name: sort_by
              description: field to sort by, supported fields action_date, -action_date
              required: false
              type: string
              default: null
        responses:
            200:
                description: Mapped projects found
            404:
                description: No mapped projects found
            500:
                description: Internal Server Error
        """
        try:
            status = request.args.get("taskStatus")
            project_id = int(request.args.get("project_id", 0))
            start_date = (
                date_parse(request.args.get("start_date"))
                if request.args.get("start_date")
                else None
            )
            end_date = (
                date_parse(request.args.get("end_date"))
                if request.args.get("end_date")
                else None
            )
            sort_by = request.args.get("sort_by")

            tasks = UserService.get_tasks_dto(
                tm.authenticated_user_id,
                project_id=project_id,
                status=status,
                start_date=start_date,
                end_date=end_date,
                sort_by=sort_by,
            )
            return tasks.to_primitive(), 200
        except NotFound:
            return {"Error": "User or tasks not found"}, 404
        except Exception as e:
            error_msg = f"User GET - unhandled error: {str(e)}"
            current_app.logger.critical(error_msg)
            return {"error": error_msg}, 500

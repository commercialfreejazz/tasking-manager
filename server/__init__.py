import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, current_app, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from flask_oauthlib.client import OAuth
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from server.config import EnvironmentConfig


def format_url(endpoint):
    parts = "/".join([i for i in endpoint.split("/") if i])
    return "/api/{}/{}/".format(EnvironmentConfig.API_VERSION, parts)


db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()

osm = oauth.remote_app("osm", app_key="OSM_OAUTH_SETTINGS")

# Import all models so that they are registered with SQLAlchemy
from server.models.postgis import *  # noqa


def create_app(env=None):
    """
    Bootstrap function to initialise the Flask app and config
    :return: Initialised Flask app
    """

    app = Flask(
        __name__,
        static_folder="../frontend/build/static",
        template_folder="../frontend/build",
    )

    # Load configuration options from environment
    app.config.from_object(f"server.config.EnvironmentConfig")

    # Enable logging to files
    initialise_logger(app)
    app.logger.info(f"Starting up a new Tasking Manager application")

    # Connect to database
    app.logger.debug(f"Connecting to the databse")
    db.init_app(app)
    migrate.init_app(app, db)

    app.logger.debug(f"Initialising frontend routes")

    # Main route to frontend
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/<path:text>")
    def assets(text):
        if "service-worker.js" in text:
            return send_from_directory(app.template_folder, text)
        elif "precache-manifest" in text:
            return send_from_directory(app.template_folder, text)
        elif "manifest.json" in text:
            return send_from_directory(app.template_folder, text)
        elif "favicon" in text:
            return send_from_directory(app.template_folder, text)
        else:
            return render_template("index.html")

    # Route to Swagger UI
    @app.route("/api-docs/")
    def api():
        api_url = current_app.config["API_DOCS_URL"]
        return render_template("swagger.html", doc_link=api_url)

    # Add paths to API endpoints
    add_api_endpoints(app)

    # Enables CORS on all API routes, meaning API is callable from anywhere
    CORS(app)

    # Add basic oauth setup
    app.secret_key = app.config[
        "SECRET_KEY"
    ]  # Required by itsdangeroud, Flask-OAuthlib for creating entropy
    oauth.init_app(app)

    return app


def initialise_logger(app):
    """
    Read environment config then initialise a 2MB rotating log.  Prod Log Level can be reduced to help diagnose Prod
    only issues.
    """
    log_dir = app.config["LOG_DIR"]
    log_level = app.config["LOG_LEVEL"]
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = RotatingFileHandler(
        log_dir + "/tasking-manager.log", "a", 2 * 1024 * 1024, 3
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)


def initialise_counters(app):
    """ Initialise homepage counters so that users don't see 0 users on first load of application"""
    from server.services.stats_service import StatsService

    with app.app_context():
        StatsService.get_homepage_stats()


def add_api_endpoints(app):
    """
    Define the routes the API exposes using Flask-Restful.
    """
    app.logger.debug("Adding routes to API endpoints")
    api = Api(app)

    # Projects API import
    from server.api.projects.resources import (
        ProjectsRestAPI,
        ProjectsAllAPI,
        ProjectsQueriesBboxAPI,
        ProjectsQueriesOwnerAPI,
        ProjectsQueriesTouchedAPI,
        ProjectsQueriesSummaryAPI,
        ProjectsQueriesNoGeometriesAPI,
        ProjectsQueriesNoTasksAPI,
        ProjectsQueriesAoiAPI,
        ProjectsQueriesFeaturedAPI,
    )
    from server.api.projects.activities import (
        ProjectsActivitiesAPI,
        ProjectsLastActivitiesAPI,
    )
    from server.api.projects.contributions import (
        ProjectsContributionsAPI,
        ProjectsContributionsQueriesDayAPI,
    )
    from server.api.projects.statistics import (
        ProjectsStatisticsAPI,
        ProjectsStatisticsQueriesUsernameAPI,
        ProjectsStatisticsQueriesPopularAPI,
    )
    from server.api.projects.teams import ProjectsTeamsAPI
    from server.api.projects.campaigns import ProjectsCampaignsAPI
    from server.api.projects.actions import (
        ProjectsActionsTransferAPI,
        ProjectsActionsMessageContributorsAPI,
        ProjectsActionsFeatureAPI,
        ProjectsActionsUnFeatureAPI,
        ProjectsActionsSetInterestsAPI,
    )

    from server.api.projects.favorites import ProjectFavoriteAPI

    # Tasks API import
    from server.api.tasks.resources import (
        TasksRestAPI,
        TasksQueriesJsonAPI,
        TasksQueriesXmlAPI,
        TasksQueriesGpxAPI,
        TasksQueriesAoiAPI,
        TasksQueriesOwnLockedAPI,
        TasksQueriesOwnLockedDetailsAPI,
        TasksQueriesMappedAPI,
        TasksQueriesOwnInvalidatedAPI,
    )
    from server.api.tasks.actions import (
        TasksActionsMappingLockAPI,
        TasksActionsMappingStopAPI,
        TasksActionsMappingUnlockAPI,
        TasksActionsMappingUndoAPI,
        TasksActionsValidationLockAPI,
        TasksActionsValidationStopAPI,
        TasksActionsValidationUnlockAPI,
        TasksActionsMapAllAPI,
        TasksActionsValidateAllAPI,
        TasksActionsInvalidateAllAPI,
        TasksActionsResetBadImageryAllAPI,
        TasksActionsResetAllAPI,
        TasksActionsSplitAPI,
    )

    # Comments API impor
    from server.api.comments.resources import (
        CommentsProjectsRestAPI,
        CommentsTasksRestAPI,
    )

    # Annotations API import
    from server.api.annotations.resources import AnnotationsRestAPI

    # Issues API import
    from server.api.issues.resources import IssuesRestAPI, IssuesAllAPI

    # Interests API import
    from server.api.interests.resources import InterestsRestAPI, InterestsAllAPI

    # Licenses API import
    from server.api.licenses.resources import LicensesRestAPI, LicensesAllAPI
    from server.api.licenses.actions import LicensesActionsAcceptAPI

    # Campaigns API endpoint
    from server.api.campaigns.resources import CampaignsRestAPI, CampaignsAllAPI

    # Organisations API endpoint
    from server.api.organisations.resources import (
        OrganisationsRestAPI,
        OrganisationsAllAPI,
    )
    from server.api.organisations.campaigns import OrganisationsCampaignsAPI

    # Countries API endpoint
    from server.api.countries.resources import CountriesRestAPI

    # Teams API endpoint
    from server.api.teams.resources import TeamsRestAPI, TeamsAllAPI
    from server.api.teams.actions import TeamsActionsJoinAPI, TeamsActionsLeaveAPI

    # Notifications API endpoint
    from server.api.notifications.resources import (
        NotificationsRestAPI,
        NotificationsAllAPI,
        NotificationsQueriesCountUnreadAPI,
    )
    from server.api.notifications.actions import NotificationsActionsDeleteMultipleAPI

    # Users API endpoint
    from server.api.users.resources import (
        UsersRestAPI,
        UsersAllAPI,
        UsersQueriesUsernameAPI,
        UsersQueriesUsernameFilterAPI,
        UserFavoritesAPI,
        UserRecommendedProjectsAPI,
        UserInterestsAPI,
    )
    from server.api.users.tasks import UsersTasksAPI
    from server.api.users.actions import (
        UsersActionsSetUsersAPI,
        UsersActionsSetLevelAPI,
        UsersActionsSetRoleAPI,
        UsersActionsSetExpertModeAPI,
        UsersActionsVerifyEmailAPI,
        UsersActionsRegisterEmailAPI,
        UsersActionsSetInterestsAPI,
    )
    from server.api.users.openstreetmap import UsersOpenStreetMapAPI
    from server.api.users.statistics import (
        UsersStatisticsAPI,
        UsersStatisticsInterestsAPI,
    )

    # System API endpoint
    from server.api.system.general import (
        SystemDocsAPI,
        SystemHeartbeatAPI,
        SystemLanguagesAPI,
        SystemContactAdminRestAPI,
    )
    from server.api.system.statistics import SystemStatisticsAPI
    from server.api.system.authentication import (
        SystemAuthenticationEmailAPI,
        SystemAuthenticationLoginAPI,
        SystemAuthenticationCallbackAPI,
    )
    from server.api.system.applications import SystemApplicationsRestAPI

    # Projects REST endpoint
    api.add_resource(ProjectsAllAPI, format_url("projects/"), methods=["GET"])
    api.add_resource(
        ProjectsRestAPI,
        format_url("projects/"),
        endpoint="create_project",
        methods=["POST"],
    )
    api.add_resource(
        ProjectsRestAPI,
        format_url("projects/<int:project_id>/"),
        methods=["GET", "PATCH", "DELETE"],
    )

    # Projects queries endoints (TODO: Refactor them into the REST endpoints)
    api.add_resource(ProjectsQueriesBboxAPI, format_url("projects/queries/bbox/"))
    api.add_resource(
        ProjectsQueriesOwnerAPI, format_url("projects/queries/myself/owner/")
    )
    api.add_resource(
        ProjectsQueriesTouchedAPI,
        format_url("projects/queries/<string:username>/touched/"),
    )
    api.add_resource(
        ProjectsQueriesSummaryAPI,
        format_url("projects/<int:project_id>/queries/summary/"),
    )
    api.add_resource(
        ProjectsQueriesNoGeometriesAPI,
        format_url("projects/<int:project_id>/queries/nogeometries/"),
    )
    api.add_resource(
        ProjectsQueriesNoTasksAPI,
        format_url("projects/<int:project_id>/queries/notasks/"),
    )
    api.add_resource(
        ProjectsQueriesAoiAPI, format_url("projects/<int:project_id>/queries/aoi/")
    )
    api.add_resource(
        ProjectsQueriesFeaturedAPI, format_url("projects/queries/featured/")
    )

    # Projects' addtional resources
    api.add_resource(
        ProjectsActivitiesAPI, format_url("projects/<int:project_id>/activities/")
    )
    api.add_resource(
        ProjectsLastActivitiesAPI,
        format_url("projects/<int:project_id>/activities/latest/"),
    )
    api.add_resource(
        ProjectsContributionsAPI, format_url("projects/<int:project_id>/contributions/")
    )
    api.add_resource(
        ProjectsContributionsQueriesDayAPI,
        format_url("projects/<int:project_id>/contributions/queries/day/"),
    )
    api.add_resource(
        ProjectsStatisticsAPI, format_url("projects/<int:project_id>/statistics/")
    )

    api.add_resource(
        ProjectsStatisticsQueriesUsernameAPI,
        format_url("projects/<int:project_id>/statistics/queries/<string:username>/"),
    )

    api.add_resource(
        ProjectsStatisticsQueriesPopularAPI, format_url("projects/queries/popular/")
    )

    api.add_resource(
        ProjectsTeamsAPI,
        format_url("projects/<int:project_id>/teams/"),
        endpoint="get_all_project_teams",
        methods=["GET"],
    )
    api.add_resource(
        ProjectsTeamsAPI,
        "/api/v2/projects/<int:project_id>/teams/<int:team_id>/",
        methods=["POST", "DELETE", "PATCH"],
    )
    api.add_resource(
        ProjectsCampaignsAPI,
        format_url("projects/<int:project_id>/campaigns/"),
        endpoint="get_all_project_campaigns",
        methods=["GET"],
    )
    api.add_resource(
        ProjectsCampaignsAPI,
        format_url("projects/<int:project_id>/campaigns/<int:campaign_id>/"),
        endpoint="assign_remove_campaign_to_project",
        methods=["POST", "DELETE"],
    )

    # Projects actions endoints
    api.add_resource(
        ProjectsActionsMessageContributorsAPI,
        format_url("projects/<int:project_id>/actions/message-contributors/"),
    )
    api.add_resource(
        ProjectsActionsTransferAPI,
        format_url("projects/<int:project_id>/actions/transfer-ownership/"),
    )
    api.add_resource(
        ProjectsActionsFeatureAPI,
        format_url("projects/<int:project_id>/actions/feature/"),
    )
    api.add_resource(
        ProjectsActionsUnFeatureAPI,
        format_url("projects/<int:project_id>/actions/remove-feature/"),
        methods=["POST"],
    )

    api.add_resource(
        ProjectFavoriteAPI,
        format_url("projects/<int:project_id>/favorite/"),
        methods=["GET", "POST", "DELETE"],
    )

    api.add_resource(
        ProjectsActionsSetInterestsAPI,
        format_url("projects/<int:project_id>/actions/set-interests/"),
        methods=["POST"],
    )

    api.add_resource(
        UsersActionsSetInterestsAPI,
        format_url("users/me/actions/set-interests/"),
        endpoint="create_user_interest",
        methods=["POST"],
    )

    api.add_resource(
        UsersStatisticsInterestsAPI,
        format_url("users/<int:user_id>/statistics/interests/"),
        methods=["GET"],
    )

    api.add_resource(
        InterestsAllAPI,
        format_url("interests/"),
        endpoint="create_interest",
        methods=["POST", "GET"],
    )
    api.add_resource(
        InterestsRestAPI,
        format_url("interests/<int:interest_id>/"),
        methods=["PATCH", "DELETE"],
    )

    # Tasks REST endpoint
    api.add_resource(
        TasksRestAPI, format_url("projects/<int:project_id>/tasks/<int:task_id>/")
    )

    # Tasks queries endoints (TODO: Refactor them into the REST endpoints)
    api.add_resource(
        TasksQueriesJsonAPI, format_url("projects/<int:project_id>/tasks/")
    )
    api.add_resource(
        TasksQueriesXmlAPI, format_url("projects/<int:project_id>/tasks/queries/xml/")
    )
    api.add_resource(
        TasksQueriesGpxAPI, format_url("projects/<int:project_id>/tasks/queries/gpx/")
    )
    api.add_resource(
        TasksQueriesAoiAPI, format_url("projects/<int:project_id>/tasks/queries/aoi/")
    )
    api.add_resource(
        TasksQueriesOwnLockedAPI, format_url("projects/tasks/queries/own/locked/")
    )
    api.add_resource(
        TasksQueriesOwnLockedDetailsAPI,
        format_url("projects/<int:project_id>/tasks/queries/own/locked/details/"),
    )
    api.add_resource(
        TasksQueriesMappedAPI,
        format_url("projects/<int:project_id>/tasks/queries/mapped/"),
    )
    api.add_resource(
        TasksQueriesOwnInvalidatedAPI,
        format_url("projects/<int:project_id>/tasks/queries/own/invalidated/"),
    )

    # Tasks actions endoints
    api.add_resource(
        TasksActionsMappingLockAPI,
        format_url(
            "projects/<int:project_id>/tasks/actions/lock-for-mapping/<int:task_id>/"
        ),
    )
    api.add_resource(
        TasksActionsMappingStopAPI,
        format_url(
            "projects/<int:project_id>/tasks/actions/stop-mapping/<int:task_id>/"
        ),
    )
    api.add_resource(
        TasksActionsMappingUnlockAPI,
        format_url(
            "projects/<int:project_id>/tasks/actions/unlock-after-mapping/<int:task_id>/"
        ),
    )
    api.add_resource(
        TasksActionsMappingUndoAPI,
        format_url(
            "projects/<int:project_id>/tasks/actions/undo-last-action/<int:task_id>/"
        ),
    )
    api.add_resource(
        TasksActionsValidationLockAPI,
        format_url("projects/<int:project_id>/tasks/actions/lock-for-validation/"),
    )
    api.add_resource(
        TasksActionsValidationStopAPI,
        format_url("projects/<int:project_id>/tasks/actions/stop-validation/"),
    )
    api.add_resource(
        TasksActionsValidationUnlockAPI,
        format_url("projects/<int:project_id>/tasks/actions/unlock-after-validation/"),
    )
    api.add_resource(
        TasksActionsMapAllAPI,
        format_url("projects/<int:project_id>/tasks/actions/map-all/"),
    )
    api.add_resource(
        TasksActionsValidateAllAPI,
        format_url("projects/<int:project_id>/tasks/actions/validate-all/"),
    )
    api.add_resource(
        TasksActionsInvalidateAllAPI,
        format_url("projects/<int:project_id>/tasks/actions/invalidate-all/"),
    )
    api.add_resource(
        TasksActionsResetBadImageryAllAPI,
        format_url("projects/<int:project_id>/tasks/actions/reset-all-badimagery/"),
    )
    api.add_resource(
        TasksActionsResetAllAPI,
        format_url("projects/<int:project_id>/tasks/actions/reset-all/"),
    )
    api.add_resource(
        TasksActionsSplitAPI,
        format_url("projects/<int:project_id>/tasks/actions/split/<int:task_id>/"),
    )

    # Comments REST endoints
    api.add_resource(
        CommentsProjectsRestAPI,
        format_url("projects/<int:project_id>/comments/"),
        methods=["GET", "POST"],
    )
    api.add_resource(
        CommentsTasksRestAPI,
        format_url("projects/<int:project_id>/comments/tasks/<int:task_id>/"),
        methods=["GET", "POST"],
    )

    # Annotations REST endoints
    api.add_resource(
        AnnotationsRestAPI,
        format_url("projects/<int:project_id>/annotations/<string:annotation_type>/"),
        format_url("projects/<int:project_id>/annotations/"),
        methods=["GET", "POST"],
    )

    # Issues REST endpoints
    api.add_resource(
        IssuesAllAPI, format_url("tasks/issues/categories/"), methods=["GET", "POST"]
    )
    api.add_resource(
        IssuesRestAPI,
        format_url("tasks/issues/categories/<int:category_id>/"),
        methods=["GET", "PATCH", "DELETE"],
    )

    # Licenses REST endpoints
    api.add_resource(LicensesAllAPI, format_url("licenses/"))
    api.add_resource(
        LicensesRestAPI,
        format_url("licenses/"),
        endpoint="create_license",
        methods=["POST"],
    )
    api.add_resource(
        LicensesRestAPI,
        format_url("licenses/<int:license_id>/"),
        methods=["GET", "PATCH", "DELETE"],
    )

    # Licenses actions endpoint
    api.add_resource(
        LicensesActionsAcceptAPI,
        format_url("licenses/<int:license_id>/actions/accept-for-me/"),
    )

    # Countries REST endpoints
    api.add_resource(CountriesRestAPI, format_url("countries/"))

    # Organisations REST endpoints
    api.add_resource(OrganisationsAllAPI, format_url("organisations/"))
    api.add_resource(
        OrganisationsRestAPI,
        format_url("organisations/"),
        endpoint="create_organisation",
        methods=["POST"],
    )
    api.add_resource(
        OrganisationsRestAPI,
        format_url("organisations/<int:organisation_id>/"),
        endpoint="get_organisation",
        methods=["GET"],
    )
    api.add_resource(
        OrganisationsRestAPI,
        format_url("organisations/<int:organisation_id>/"),
        methods=["PUT", "DELETE", "PATCH"],
    )

    # Organisations additional resources endpoints
    api.add_resource(
        OrganisationsCampaignsAPI,
        format_url("organisations/<int:organisation_id>/campaigns/"),
        endpoint="get_all_organisation_campaigns",
        methods=["GET"],
    )
    api.add_resource(
        OrganisationsCampaignsAPI,
        format_url("organisations/<int:organisation_id>/campaigns/<int:campaign_id>/"),
        endpoint="assign_campaign_to_organisation",
        methods=["POST", "DELETE"],
    )

    # Teams REST endpoints
    api.add_resource(TeamsAllAPI, format_url("teams"), methods=["GET"])
    api.add_resource(
        TeamsAllAPI, format_url("teams/"), endpoint="create_team", methods=["POST"]
    )
    api.add_resource(
        TeamsRestAPI,
        format_url("teams/<int:team_id>/"),
        methods=["GET", "PUT", "DELETE", "PATCH"],
    )

    # Teams actions endpoints
    api.add_resource(
        TeamsActionsJoinAPI,
        format_url("teams/<int:team_id>/actions/join/"),
        methods=["POST", "PUT"],
    )
    api.add_resource(
        TeamsActionsLeaveAPI,
        format_url("teams/<int:team_id>/actions/leave/"),
        endpoint="leave_team",
        methods=["POST"],
    )

    # Campaigns REST endpoints
    api.add_resource(
        CampaignsAllAPI,
        format_url("campaigns/"),
        endpoint="get_all_campaign",
        methods=["GET"],
    )
    api.add_resource(
        CampaignsAllAPI,
        format_url("campaigns/"),
        endpoint="create_campaign",
        methods=["POST"],
    )
    api.add_resource(
        CampaignsRestAPI,
        format_url("campaigns/<int:campaign_id>/"),
        methods=["GET", "PATCH", "DELETE"],
    )

    # Notifications REST endpoints
    api.add_resource(
        NotificationsRestAPI, format_url("notifications/<int:message_id>/")
    )
    api.add_resource(NotificationsAllAPI, format_url("notifications/"))
    api.add_resource(
        NotificationsQueriesCountUnreadAPI,
        format_url("notifications/queries/own/count-unread/"),
    )

    # Notifications Actions endpoints
    api.add_resource(
        NotificationsActionsDeleteMultipleAPI,
        format_url("notifications/delete-multiple/"),
        methods=["DELETE"],
    )

    # Users REST endpoint
    api.add_resource(UsersAllAPI, format_url("users/"))
    api.add_resource(UsersRestAPI, format_url("users/<int:user_id>/"))
    api.add_resource(
        UsersQueriesUsernameFilterAPI,
        format_url("users/queries/filter/<string:username>/"),
    )
    api.add_resource(
        UsersQueriesUsernameAPI, format_url("users/queries/<string:username>/")
    )
    api.add_resource(UserFavoritesAPI, format_url("users/queries/favorites/"))

    # Users Actions endpoint
    api.add_resource(UsersActionsSetUsersAPI, format_url("users/me/actions/set-user/"))

    api.add_resource(
        UsersActionsSetLevelAPI,
        format_url("users/<string:username>/actions/set-level/<string:level>/"),
    )
    api.add_resource(
        UsersActionsSetRoleAPI,
        format_url("users/<string:username>/actions/set-role/<string:role>/"),
    )
    api.add_resource(
        UsersActionsSetExpertModeAPI,
        format_url(
            "users/<string:username>/actions/set-expert-mode/<string:is_expert>/"
        ),
    )

    api.add_resource(UsersTasksAPI, format_url("users/<int:user_id>/tasks/"))
    api.add_resource(
        UsersActionsVerifyEmailAPI, format_url("users/me/actions/verify-email/")
    )
    api.add_resource(
        UsersActionsRegisterEmailAPI, format_url("users/actions/register/")
    )

    # Users Statistics endpoint
    api.add_resource(
        UsersStatisticsAPI, format_url("users/<string:username>/statistics/")
    )

    # User RecommendedProjects endpoint
    api.add_resource(
        UserRecommendedProjectsAPI,
        format_url("users/<string:username>/recommended-projects/"),
    )

    # User Interests endpoint
    api.add_resource(
        UserInterestsAPI, format_url("users/<string:username>/queries/interests/")
    )

    # Users openstreetmap endpoint
    api.add_resource(
        UsersOpenStreetMapAPI, format_url("users/<string:username>/openstreetmap/")
    )

    # System endpoint
    api.add_resource(SystemDocsAPI, format_url("system/docs/json/"))
    api.add_resource(SystemHeartbeatAPI, format_url("system/heartbeat/"))
    api.add_resource(SystemLanguagesAPI, format_url("system/languages/"))
    api.add_resource(SystemStatisticsAPI, format_url("system/statistics/"))
    api.add_resource(
        SystemAuthenticationLoginAPI, format_url("system/authentication/login/")
    )
    api.add_resource(
        SystemAuthenticationCallbackAPI, format_url("system/authentication/callback/")
    )
    api.add_resource(
        SystemAuthenticationEmailAPI, format_url("system/authentication/email/")
    )
    api.add_resource(
        SystemApplicationsRestAPI,
        format_url("system/authentication/applications/"),
        methods=["POST", "GET"],
    )
    api.add_resource(
        SystemApplicationsRestAPI,
        format_url("system/authentication/applications/<string:application_key>/"),
        endpoint="delete_application",
        methods=["DELETE"],
    )
    api.add_resource(
        SystemApplicationsRestAPI,
        format_url("system/authentication/applications/<string:application_key>/"),
        endpoint="check_application",
        methods=["PATCH"],
    )
    api.add_resource(
        SystemContactAdminRestAPI, "/api/v2/system/contact-admin/", methods=["POST"]
    )

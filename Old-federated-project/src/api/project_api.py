"""
Project-Level Debate Context API
================================

Flask-RESTX API endpoints for project management and aggregated metrics.
"""

from flask import Blueprint, request, jsonify
from flask_restx import Api, Resource, fields
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, and_
from datetime import datetime
import uuid
from typing import Dict, List, Optional

# Mock imports - replace with actual imports in production
# from models.project_models import DebateProject, ProjectSubjectLink, ProjectMetrics
# from models.debate_models import Debate, Scenario
# from database import engine

project_api = Blueprint('project_api', __name__)
api = Api(project_api, doc='/projects/docs/', title='Project Context API', 
          description='Project-level containers for debate series and governance programs')

# API Models for documentation
project_model = api.model('Project', {
    'id': fields.String(description='Project UUID'),
    'external_id': fields.String(description='Human-friendly ID (e.g., DV-001)'),
    'name': fields.String(required=True, description='Project name'),
    'description': fields.String(description='Project description'),
    'sponsor': fields.String(description='Sponsoring organization'),
    'status': fields.String(enum=['planned', 'active', 'on_hold', 'complete']),
    'start_date': fields.DateTime(description='Project start date'),
    'end_date': fields.DateTime(description='Project end date'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp')
})

project_create_model = api.model('ProjectCreate', {
    'external_id': fields.String(description='Optional human-friendly ID'),
    'name': fields.String(required=True, description='Project name'),
    'description': fields.String(description='Project description'),
    'sponsor': fields.String(description='Sponsoring organization'),
    'status': fields.String(enum=['planned', 'active', 'on_hold', 'complete'], default='planned'),
    'start_date': fields.DateTime(description='Project start date'),
    'end_date': fields.DateTime(description='Project end date')
})

subject_link_model = api.model('SubjectLink', {
    'class_code': fields.String(required=True, description='LCC class code'),
    'label': fields.String(description='Subject label'),
    'relevance_score': fields.Float(description='Relevance score (0.0-1.0)')
})

metrics_model = api.model('ProjectMetrics', {
    'debate_count': fields.Integer(description='Total debates in project'),
    'scenario_count': fields.Integer(description='Total scenarios in project'),
    'open_debates': fields.Integer(description='Currently open debates'),
    'closed_debates': fields.Integer(description='Completed debates'),
    'average_consensus': fields.Float(description='Average consensus score'),
    'mismatch_events': fields.Integer(description='Total mismatch events'),
    'total_participants': fields.Integer(description='Total unique participants'),
    'last_refresh': fields.DateTime(description='Last metrics refresh')
})

debate_summary_model = api.model('DebateSummary', {
    'id': fields.String(description='Debate UUID'),
    'title': fields.String(description='Debate title'),
    'status': fields.String(description='Debate status'),
    'confidence': fields.Float(description='Confidence score'),
    'start_time': fields.DateTime(description='Debate start time'),
    'end_time': fields.DateTime(description='Debate end time'),
    'primary_subject': fields.String(description='Primary LCC subject code')
})

project_detail_model = api.model('ProjectDetail', {
    'project': fields.Nested(project_model),
    'subjects': fields.List(fields.Nested(subject_link_model)),
    'metrics': fields.Nested(metrics_model)
})

@api.route('/projects')
class ProjectList(Resource):
    @api.doc('list_projects')
    @api.marshal_list_with(project_model)
    @api.param('status', 'Filter by project status')
    @api.param('sponsor', 'Filter by sponsor')
    @api.param('subject', 'Filter by LCC subject code')
    def get(self):
        """List all debate projects with optional filtering."""
        try:
            # Mock implementation - replace with actual database queries
            projects = []
            
            # Example mock data
            mock_project = {
                'id': str(uuid.uuid4()),
                'external_id': 'DV-001',
                'name': 'Value-Based Care Debate Series',
                'description': 'Cross-team governance program for VBHC policy development',
                'sponsor': 'Regulatory Council',
                'status': 'active',
                'start_date': '2025-09-01T12:00:00Z',
                'end_date': None,
                'created_at': '2025-09-30T10:00:00Z',
                'updated_at': '2025-09-30T15:30:00Z'
            }
            projects.append(mock_project)
            
            # Apply filters from query parameters
            status_filter = request.args.get('status')
            sponsor_filter = request.args.get('sponsor')
            subject_filter = request.args.get('subject')
            
            # Filter logic would go here
            
            return projects, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('create_project')
    @api.expect(project_create_model)
    @api.marshal_with(project_model)
    def post(self):
        """Create a new debate project."""
        try:
            data = request.get_json()
            
            # Mock implementation - replace with actual database creation
            new_project = {
                'id': str(uuid.uuid4()),
                'external_id': data.get('external_id'),
                'name': data['name'],
                'description': data.get('description'),
                'sponsor': data.get('sponsor'),
                'status': data.get('status', 'planned'),
                'start_date': data.get('start_date'),
                'end_date': data.get('end_date'),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            return new_project, 201
            
        except Exception as e:
            return {'error': str(e)}, 500

@api.route('/projects/<string:project_id>')
class ProjectDetail(Resource):
    @api.doc('get_project')
    @api.marshal_with(project_detail_model)
    def get(self, project_id):
        """Get detailed project information including subjects and metrics."""
        try:
            # Mock implementation
            project_data = {
                'project': {
                    'id': project_id,
                    'external_id': 'DV-001',
                    'name': 'Value-Based Care Debate Series',
                    'description': 'Cross-team governance program for VBHC policy development',
                    'sponsor': 'Regulatory Council',
                    'status': 'active',
                    'start_date': '2025-09-01T12:00:00Z',
                    'end_date': None,
                    'created_at': '2025-09-30T10:00:00Z',
                    'updated_at': '2025-09-30T15:30:00Z'
                },
                'subjects': [
                    {'class_code': 'RA', 'label': 'Public health', 'relevance_score': 0.95},
                    {'class_code': 'HJ', 'label': 'Public finance', 'relevance_score': 0.85}
                ],
                'metrics': {
                    'debate_count': 4,
                    'scenario_count': 6,
                    'open_debates': 2,
                    'closed_debates': 2,
                    'average_consensus': 0.91,
                    'mismatch_events': 3,
                    'total_participants': 12,
                    'last_refresh': '2025-09-30T22:01:00Z'
                }
            }
            
            return project_data, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('update_project')
    @api.expect(project_create_model)
    @api.marshal_with(project_model)
    def patch(self, project_id):
        """Update project details."""
        try:
            data = request.get_json()
            
            # Mock implementation - would update database record
            updated_project = {
                'id': project_id,
                'name': data.get('name', 'Value-Based Care Debate Series'),
                'description': data.get('description'),
                'sponsor': data.get('sponsor'),
                'status': data.get('status'),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            return updated_project, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

@api.route('/projects/<string:project_id>/debates')
class ProjectDebates(Resource):
    @api.doc('get_project_debates')
    @api.marshal_list_with(debate_summary_model)
    def get(self, project_id):
        """Get all debates associated with this project."""
        try:
            # Mock implementation
            debates = [
                {
                    'id': str(uuid.uuid4()),
                    'title': 'Regulatory compliance framework',
                    'status': 'closed',
                    'confidence': 0.95,
                    'start_time': '2025-09-15T18:00:00Z',
                    'end_time': '2025-09-15T19:30:00Z',
                    'primary_subject': 'RA'
                },
                {
                    'id': str(uuid.uuid4()),
                    'title': 'Budget allocation priorities',
                    'status': 'active',
                    'confidence': 0.87,
                    'start_time': '2025-09-30T14:00:00Z',
                    'end_time': None,
                    'primary_subject': 'HJ'
                }
            ]
            
            return debates, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

@api.route('/projects/<string:project_id>/metrics')
class ProjectMetricsAPI(Resource):
    @api.doc('get_project_metrics')
    @api.marshal_with(metrics_model)
    def get(self, project_id):
        """Get aggregated metrics for the project."""
        try:
            # Mock implementation - would calculate from database
            metrics = {
                'debate_count': 4,
                'scenario_count': 6,
                'open_debates': 2,
                'closed_debates': 2,
                'average_consensus': 0.91,
                'mismatch_events': 3,
                'total_participants': 12,
                'last_refresh': '2025-09-30T22:01:00Z'
            }
            
            return metrics, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('refresh_project_metrics')
    def post(self, project_id):
        """Trigger a refresh of project metrics."""
        try:
            # Mock implementation - would trigger background job
            result = {
                'message': 'Metrics refresh initiated',
                'project_id': project_id,
                'refresh_time': datetime.utcnow().isoformat()
            }
            
            return result, 202
            
        except Exception as e:
            return {'error': str(e)}, 500

@api.route('/projects/<string:project_id>/subjects')
class ProjectSubjects(Resource):
    @api.doc('get_project_subjects')
    @api.marshal_list_with(subject_link_model)
    def get(self, project_id):
        """Get LCC subject codes associated with this project."""
        try:
            # Mock implementation
            subjects = [
                {'class_code': 'RA', 'label': 'Public health', 'relevance_score': 0.95},
                {'class_code': 'HJ', 'label': 'Public finance', 'relevance_score': 0.85},
                {'class_code': 'HD', 'label': 'Economic conditions', 'relevance_score': 0.75}
            ]
            
            return subjects, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

    @api.doc('add_project_subject')
    @api.expect(subject_link_model)
    def post(self, project_id):
        """Attach an LCC subject code to the project."""
        try:
            data = request.get_json()
            
            # Mock implementation - would create database record
            result = {
                'message': 'Subject linked to project',
                'project_id': project_id,
                'class_code': data['class_code'],
                'created_at': datetime.utcnow().isoformat()
            }
            
            return result, 201
            
        except Exception as e:
            return {'error': str(e)}, 500

@api.route('/projects/<string:project_id>/subjects/<string:class_code>')
class ProjectSubjectDetail(Resource):
    @api.doc('remove_project_subject')
    def delete(self, project_id, class_code):
        """Remove subject link from project."""
        try:
            # Mock implementation - would delete database record
            result = {
                'message': 'Subject unlinked from project',
                'project_id': project_id,
                'class_code': class_code,
                'removed_at': datetime.utcnow().isoformat()
            }
            
            return result, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

@api.route('/projects/<string:project_id>/timeline')
class ProjectTimeline(Resource):
    @api.doc('get_project_timeline')
    def get(self, project_id):
        """Get chronological timeline of project events."""
        try:
            # Mock implementation
            timeline = [
                {
                    'timestamp': '2025-09-01T12:00:00Z',
                    'event_type': 'project_created',
                    'description': 'Project initiated',
                    'metadata': {'sponsor': 'Regulatory Council'}
                },
                {
                    'timestamp': '2025-09-15T18:00:00Z',
                    'event_type': 'debate_started',
                    'description': 'Regulatory compliance debate began',
                    'metadata': {'debate_id': str(uuid.uuid4()), 'participants': 6}
                },
                {
                    'timestamp': '2025-09-15T19:30:00Z',
                    'event_type': 'debate_completed',
                    'description': 'Regulatory compliance debate concluded',
                    'metadata': {'consensus_score': 0.95, 'duration_minutes': 90}
                }
            ]
            
            return timeline, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

# Utility functions for metrics calculation
def calculate_project_metrics(project_id: str) -> Dict:
    """Calculate aggregated metrics for a project."""
    # Mock implementation - replace with actual database queries
    return {
        'debate_count': 4,
        'scenario_count': 6,
        'open_debates': 2,
        'closed_debates': 2,
        'average_consensus': 0.91,
        'mismatch_events': 3,
        'total_participants': 12,
        'last_refresh': datetime.utcnow().isoformat()
    }

def get_project_subjects_with_enrichment(project_id: str) -> List[Dict]:
    """Get project subjects with FAST enrichments."""
    # Mock implementation - would join with LCC-FAST crosswalk
    return [
        {
            'class_code': 'RA',
            'label': 'Public health',
            'relevance_score': 0.95,
            'fast_subjects': [
                {'fast_id': 'fst01062958', 'heading': 'Public health', 'facet_type': 'topical'}
            ]
        }
    ]

if __name__ == '__main__':
    print("Project Context API Endpoints:")
    print("==============================")
    print("GET    /projects                    - List projects")
    print("POST   /projects                    - Create project")
    print("GET    /projects/{id}               - Project details")
    print("PATCH  /projects/{id}               - Update project")
    print("GET    /projects/{id}/debates       - Project debates")
    print("GET    /projects/{id}/metrics       - Project metrics")
    print("POST   /projects/{id}/metrics       - Refresh metrics")
    print("GET    /projects/{id}/subjects      - Project subjects")
    print("POST   /projects/{id}/subjects      - Add subject")
    print("DELETE /projects/{id}/subjects/{code} - Remove subject")
    print("GET    /projects/{id}/timeline      - Project timeline")
    print()
    print("Ready for integration with main Flask app!")
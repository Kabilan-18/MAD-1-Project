from flask_app import app, db
from flask import make_response, request, send_file
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flask_app.models import Section, Book
from werkzeug.exceptions import HTTPException
import json

api = Api(app)

section_args = reqparse.RequestParser()
section_args.add_argument('section_id', type=int)
section_args.add_argument('section_name', type=str)
section_args.add_argument('section_description', type=str)

book_args = reqparse.RequestParser()
book_args.add_argument('book_id', type=int)
book_args.add_argument('book_name', type=str)
book_args.add_argument('book_authors', type=str)
book_args.add_argument('section_id', type=int)

class Message(HTTPException):
    def __init__(self, message, status_code):
        self.response = make_response(json.dumps(message), status_code)

section_resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String
}

book_resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'authors': fields.String,
    'section_id': fields.Integer
}

class SectionResource(Resource):
    @marshal_with(section_resource_fields)
    def get(self, section_id):
        section = Section.query.get(section_id)
        if section:
            return section, 200
        else:
            raise Message('Section not found', 404)

    @marshal_with(section_resource_fields)
    def post(self):
        args = section_args.parse_args()
        section = Section(name=args['section_name'], description=args['section_description'])
        db.session.add(section)
        db.session.commit()
        return section, 201

    @marshal_with(section_resource_fields)
    def put(self, section_id):
        section = Section.query.get(section_id)
        if section:
            args = section_args.parse_args()
            section.name = args['section_name']
            section.description = args['section_description']
            db.session.commit()
            return section, 200
        else:
            raise Message('Section not found', 404)

    @marshal_with(section_resource_fields)
    def delete(self, section_id):
        section = Section.query.get(section_id)
        if section:
            db.session.delete(section)
            db.session.commit()
            return Message('Section sucessfully deleted', 204)
        else:
            raise Message('Section not found', 404)
        
class BookResource(Resource):
    @marshal_with(book_resource_fields)
    def get(self, book_id):
        book = Book.query.get(book_id)
        if book:
            return book, 200
        else:
            raise Message('Book not found', 404)

    @marshal_with(book_resource_fields)
    def put(self, book_id):
        book = Book.query.get(book_id)
        if book:
            args = book_args.parse_args()
            book.name = args['book_name']
            book.authors = args['book_authors']
            book.section_id = args['section_id']
            db.session.commit()
            return book, 200
        else:
            raise Message('Book not found', 404)

    @marshal_with(book_resource_fields)
    def delete(self, book_id):
        book = Book.query.get(book_id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return Message('Book sucessfully deleted', 204)
        else:
            raise Message('Book not found', 404)

class GraphResource(Resource):
    def get(self):
        if 'bar_chart' in str(request.url_rule):
            bar_chart_path = 'static/charts/admin_bar_chart.png'
            return send_file(bar_chart_path, mimetype='image/png')
        else:
            pie_chart_path = 'static/charts/admin_pie_chart.png' 
            return send_file(pie_chart_path, mimetype='image/png')


api.add_resource(SectionResource, '/api/section', '/api/section/<int:section_id>')
api.add_resource(BookResource, '/api/book', '/api/book/<int:book_id>')
api.add_resource(GraphResource, '/api/graph/bar_chart', '/api/graph/pie_chart')
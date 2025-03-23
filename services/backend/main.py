
from flask import Flask,jsonify
from flask_restx import Api, Resource,fields,reqparse # type: ignore
from src.utils.logger import logging
from dotenv import load_dotenv
import os
from src.utils.exception import CustomException
import sys

from src.dataflow.rag_model import generateResponse
load_dotenv('backend/backend.env',override=True)
from flask_cors import CORS


app =Flask(__name__)
CORS(app,origins="*",allow_headers="*") 
# Initialize Flask-RESTX API with Swagger support
api =Api(app, version="1.0" , title="NuBot Backend", description="Backend for NuBot")

# create a namespace 
ns=api.namespace("NuBot",descrption="namespace for Backend")
parser = reqparse.RequestParser()
# Define a request model for Swagger UI
query_model = api.model('QueryModel', {
    'query': fields.String(required=True, description="User's input query")
})
@ns.route("/")
class Main(Resource):
    @api.expect(query_model)
    @api.response(200, "Success")
    @api.response(404, "Not Found")
    @api.response(500, "Internal Server Error")
    def post(self):
        """Return a simple message"""
        try:
            parser.add_argument('query', required=True, help="Name cannot be blank!")
            args=parser.parse_args()
            logging.info("Get api called")
            query=args['query']
            logging.info("response function called")
            response=generateResponse(query)
            logging.info("Response generated successfully")
            return response
        except Exception as e:
            logging.error("Custom exception occurred: %s", str(e))
            return jsonify({"error": "An internal server error occurred", "details": str(e)})
           

if __name__=="__main__":
    PORT=os.getenv("PORT")
    app.run(host="0.0.0.0",port=PORT,debug=True)
import redis
from flask import Flask, jsonify
from flask_restx import Api, Resource, fields, reqparse
from src.utils.logger import logging
from dotenv import load_dotenv
import os
from src.utils.exception import CustomException
import sys
from src.dataflow.rag_model import generateResponse
from flask_cors import CORS

# load_dotenv('backend/backend.env', override=True)

# Connect to Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_client = redis.StrictRedis(host=redis_host, port=6379, db=0, decode_responses=True)

app = Flask(__name__)
CORS(app, origins="*", allow_headers="*")  # You may want to restrict origins in production

# Initialize Flask-RESTX API with Swagger support
api = Api(app, version="1.0", title="NuBot Backend", description="Backend for NuBot")

# Create a namespace 
ns = api.namespace("NuBot", description="Namespace for Backend")

# Define request model for Swagger UI
query_model = api.model('QueryModel', {
    'query': fields.String(required=True, description="User's input query")
})

parser = reqparse.RequestParser()

@ns.route("/")
class Main(Resource):
    @api.expect(query_model)
    @api.response(200, "Success")
    @api.response(404, "Not Found")
    @api.response(500, "Internal Server Error")
    def post(self):
        """Return a simple message"""
        try:
            parser.add_argument('query', required=True, help="Query cannot be blank!")
            args = parser.parse_args()
            logging.info("POST API called")
            query = args['query']
            
            # Check Redis for previous queries
            previous_chat = redis_client.get(query)
            if previous_chat:
                logging.info("Found previous response in Redis")
                return jsonify({"response": previous_chat})
            
            logging.info("Response function called")
            response = generateResponse(query)
            logging.info("Response generated successfully")
            
            # Store the response in Redis for future queries
            redis_client.set(query, response, ex=3600)  # Cache for 1 hour
            return jsonify({"response": response})
            
        except Exception as e:
            logging.error("Custom exception occurred: %s", str(e))
            return jsonify({"error": "An internal server error occurred", "details": str(e)})

if __name__ == "__main__":
    PORT = os.getenv("PORT", 5002)  # Default to 5002 if not set
    app.run(host='0.0.0.0', port=int(PORT), debug=True)

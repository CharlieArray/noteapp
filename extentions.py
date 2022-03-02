from flask_bcrypt import Bcrpyt
from flask_graphql_auth import GraphQLAuth
from flask_jwt_extended import JWTManager

bcrypt = Bcrypt()
auth = GraphQLAuth()
jwt = JWTManager()
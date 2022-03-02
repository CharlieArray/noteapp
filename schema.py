from models import (
    User as UserModel, Notes as NotesModel, 
    session
)

import graphene
from graphene_sqlalchemy import (
    SQLAlchemyConnectionField,
    SQLAlchemyObjectType
)
from extentions import bcrypt
from typing import Optional 
 
#types
class User(SQLAlchemyObjectType):
    class Meta: 
        model = UserModel

class Notes(SQLAlchemyObjectType):
    class Meta: 
        model = NotesModel

#registration

# defines mutation class
class createUser(graphene.Mutation):
    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        password = graphene.String()
    ok = graphene.Boolean()
    user = graphene.Field(User)


    # function that is applied once mutation is called. 
    # just a special resolver that can change data within
    def mutate(root, info, first_name, last_name, email, password):
        new_user = UserModel(
            first_name=first_name, 
            last_name=last_name, 
            email=email, 
            password=str(bcrypt.generate_password_hash(password),'utf-8')
        )
        
        # adds user to our database session
        session.add(new_user)
        # commits new user to db session so the data persists
        session.commit()
        ok = True
        #returns an instance of the create User 
        return createUser(ok=ok, user=new_user)

# add new note
class addNote(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        body = graphene.String()
    ok = graphene.Boolean()
    note = graphene.Field(Notes)

    def mutate(root, info, title, body):
        uid = info.context['uid']
        # find user based on token payload
        user = session.query(UserModel).filter_by(email=uid).first()
        new_note = NotesModel(
            title=title,
            body=body,
            user=user
        )
        session.add(new_note)
        session.commit()
        ok = True
        return addNote(ok=ok, note=new_note)

# update existing note
class updateNote(graphene.Mutation):
    class Arguments:
        note_id = graphene.Int()
        title = graphene.String()
        body = graphene.String()
    ok = graphene.Boolean()
    note = graphene.Field(Notes)

    def mutate(root, info, note_id, title: Optional[str]=None, body: Optional[str]=None):
        # find note object
        note = session.query(NotesModel).filter_by(id=note_id).first()
        #what is this logic? if title not passed in parameter for update?
        #note.body = original; body = new update
        if not title:
            note.body = body
        elif not body:
            note.title = title
        else:
            note.title = title
            note.body = body
        session.commit()
        ok = True
        note = note
        return updateNote(ok=ok, note=note)

# delete note
class deleteNote(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
    ok = graphene.Boolean()
    note = graphene.Field(Notes)

    def mutate(root, info, id):
        note = session.query(NotesModel).filter_by(id=id).first()
        session.delete(note)
        ok = True
        note = note
        session.commit()
        return deleteNote(ok=ok, note=note)

class PostAuthMutation(graphene.ObjectType):
    addNote = addNote.Field()
    updateNote = updateNote.Field()
    deleteNote = deleteNote.Field()


class PreAuthMutation(graphene.ObjectType):
    create_user = createUser.Field()

class Query(graphene.ObjectType):
    
    # what is happening?
    # find single note
    findNote = graphene.Field(Notes, id=graphene.Int())
    # get all notes by user
    user_notes = graphene.List(Notes)

    def resolve_user_notes(root, info):
        # find user with uid from token
        # what is happening?
        uid = info.context['uid']
        user = session.query(UserModel).filter_by(email = uid).first()
        return user.notes
    
    def resolve_findNote(root, info, id):
        return session.query(NotesModel).filter_by(id=id).first()


class PreAuthQuery(graphene.ObjectType):
    all_users = graphene.List(User)

    # what is happening with root and info?
    def resolve_all_users(root, info):
        return session.query(UserModel).all()

auth_required_schema = graphene.Schema(query=Query, mutation=PostAuthMutation)
schema = graphene.Schema(query=PreAuthQuery, mutation=PreAuthMutation)
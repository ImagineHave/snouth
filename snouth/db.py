import pymongo
import click
from flask import current_app, g
from flask.cli import with_appcontext

def getClient():
    """get MongoClient."""
    if not hasattr(g, 'db_client'):
        g.db_client = pymongo.MongoClient(current_app.config['MONGO_URI'])
    return g.db_client
    
    
def get_db():
    """get DB"""
    if not hasattr(g, 'db'):
        g.db = getClient().get_default_database()
    return g.db


def close_db(e=None):
    """close connection"""
    db_client = g.pop('db_client', None)
    if db_client is not None:
        db_client.close()
        
        
def init_db():
    """wipe the database"""
    db = get_db()
    collections = db.collection_names(include_system_collections=False)
    for collection in collections:
        db[collection].drop()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data."""
    init_db()
    click.echo('Initialized the database.')
        
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
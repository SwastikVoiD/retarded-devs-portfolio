from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TeamInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mission = db.Column(db.Text, nullable=True)
    what_we_do = db.Column(db.Text, nullable=True)
    why_we_do = db.Column(db.Text, nullable=True)

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    short_bio = db.Column(db.String(250), nullable=False)
    full_bio = db.Column(db.Text, nullable=True)
    contributions = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    github_link = db.Column(db.String(250), nullable=True)
    twitter_link = db.Column(db.String(250), nullable=True)
    image_url = db.Column(db.String(250), default="https://api.dicebear.com/7.x/avataaars/svg?seed=dev")
    
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    short_description = db.Column(db.String(250), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="Past") # 'Ongoing' or 'Past'
    tags = db.Column(db.String(200))
    icon = db.Column(db.String(50), default="box")
    
    # Detail page content
    overview = db.Column(db.Text, nullable=True)
    challenges = db.Column(db.Text, nullable=True)
    modifications = db.Column(db.Text, nullable=True)
    results = db.Column(db.Text, nullable=True)
    
    # Metadata
    timeline = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(100), nullable=True) # Used to specify which team members worked on this
    technologies = db.Column(db.String(200), nullable=True)
    github_link = db.Column(db.String(250), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    endpoint = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

import os
# pyrefly: ignore [missing-import]
import traceback
import markdown
from markupsafe import Markup
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from models import db, Project, AccessLog, ContactMessage, TeamMember, Blog, TeamInfo

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'retarded-devs-super-secret-key-123')

# Check for cloud database URL (Vercel/Production)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Fix older postgres:// schemas which SQLAlchemy doesn't support anymore
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to local SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'team_portfolio.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.errorhandler(Exception)
def handle_exception(e):
    # This will catch all unhandled exceptions and print the traceback to the browser
    return f"<pre>Internal Server Error\\n\\n{traceback.format_exc()}</pre>", 500

@app.template_filter('markdown')
def markdown_filter(text):
    if text:
        # extensions=['fenced_code', 'codehilite'] for code highlighting support
        return Markup(markdown.markdown(text, extensions=['fenced_code']))
    return ""

# --- Authentication Middleware ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Access Logging Middleware ---
@app.before_request
def log_request():
    if request.endpoint and not request.endpoint.startswith('static') and not request.endpoint.startswith('dashboard') and request.endpoint != 'seed':
        try:
            ip = request.remote_addr
            endpoint = request.path
            log = AccessLog(ip_address=ip, endpoint=endpoint) # type: ignore
            db.session.add(log)
            db.session.commit()
        except Exception:
            db.session.rollback()

# --- Public Routes ---
@app.route('/seed')
def seed():
    try:
        # Drop and recreate all tables to fix any schema mismatch issues (like missing 'status' column)
        db.drop_all()
        db.create_all()
        
        p1 = Project( # type: ignore
            title="Project Alpha: Core Systems",
            short_description="A complete overhaul of our backend infrastructure with 3D data visualization.",
            category="Backend",
            status="Ongoing",
            tags="Python, Flask, 3D",
            icon="server",
            overview="Project Alpha is our flagship initiative to modernize the core infrastructure.",
            challenges="The primary challenge was ensuring zero downtime during the migration.",
            modifications="We iterated through three different database sharding strategies.",
            results="Achieved a 400% increase in throughput and reduced latency by 60ms globally.",
            timeline="Q1 2026 - Present",
            role="Lead Architect",
            technologies="Python, Go, PostgreSQL, WebGL",
            github_link="https://github.com"
        )
        db.session.add(p1)
        
        p2 = Project( # type: ignore
            title="UI/UX Reimagined",
            short_description="Building a next-generation fluid presentation interface.",
            category="Frontend",
            status="Past",
            tags="UI/UX, Design",
            icon="layout",
            overview="Redesigning the portfolio to behave like a slick, immersive presentation deck.",
            challenges="Balancing heavy graphics with buttery smooth 60fps scrolling performance.",
            results="A visually stunning interface that converts visitors at a 3x higher rate.",
            timeline="Q4 2025",
            role="Frontend Developer",
            technologies="HTML5 Canvas, CSS Snap Scroll, Vanilla JS"
        )
        db.session.add(p2)
        
        t1 = TeamMember( # type: ignore
            name="Cipher",
            role="Lead Developer",
            short_bio="Specializes in backend architecture and 3D web integration. Loves building complex systems that run invisibly behind beautiful interfaces.",
            full_bio="With over a decade of experience in systems architecture, I've spent my career building highly scalable backend infrastructure for high-frequency trading platforms and massive multiplayer gaming networks. I transitioned into creative web engineering because I wanted to bridge the gap between heavy data processing and beautiful, interactive 3D frontend experiences.",
            experience="Senior Architect at TechCorp (2020-2024)\\nLead Backend Engineer at StartupX (2018-2020)\\nB.S. Computer Science",
            contributions="Architected the proprietary WebGL integration pipeline.\\nDesigned the distributed database schema.\\nMaintained 99.99% uptime during migration.",
            image_url="avatar1.png",
            github_link="https://github.com",
            twitter_link="https://linkedin.com"
        )
        t2 = TeamMember( # type: ignore
            name="Ghost",
            role="UI/UX Designer",
            short_bio="The creative mind behind the pure black aesthetic and the fluid presentation layouts. Turns raw data into visual art.",
            full_bio="Design isn't just about making things look pretty; it's about dictating how a user feels the moment the page loads. My philosophy is 'less is more, but what is there must be perfect.' I specialize in dark-mode aesthetics, brutalist typography, and fluid micro-animations that make websites feel alive.",
            experience="Lead UI/UX Designer at CreativeAgency (2021-Present)\\nFreelance Digital Artist (2019-2021)",
            contributions="Designed the global parallax 3D mesh aesthetic.\\nEngineered the CSS Snap-Scroll presentation layout.\\nCreated the minimalist branding and typography scales.",
            image_url="avatar1.png",
            twitter_link="https://twitter.com"
        )
        db.session.add_all([t1, t2])
        
        info = TeamInfo( # type: ignore
            mission="To build the most aesthetic and performant digital experiences on the web.",
            what_we_do="We specialize in deep-tech backend engineering combined with immersive, cutting-edge frontend design.",
            why_we_do="Because standard web templates are boring, and we believe in pushing the boundaries of what browsers can do."
        )
        db.session.add(info)
            
        db.session.commit()
        flash("Database completely reset and seeded with test data!", "success")
    except Exception as e:
        flash(f"Error seeding data: {str(e)}", "error")
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message_text = request.form.get('message')
        if name and email and message_text:
            msg = ContactMessage(name=name, email=email, message=message_text) # type: ignore
            db.session.add(msg)
            db.session.commit()
            flash('Thank you for reaching out! We will get back to you soon.', 'success')
        else:
            flash('Please fill out all fields.', 'error')
        return redirect(url_for('index', _anchor='contact'))
        
    featured_projects = Project.query.limit(3).all()
    latest_blogs = Blog.query.order_by(Blog.timestamp.desc()).limit(3).all()
    return render_template('index.html', projects=featured_projects, blogs=latest_blogs)

@app.route('/about')
def about():
    team_info = TeamInfo.query.first()
    members = TeamMember.query.all()
    return render_template('about.html', team_info=team_info, members=members)

@app.route('/team/<int:member_id>')
def team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    return render_template('team-member.html', member=member)

@app.route('/projects')
def projects():
    all_projects = Project.query.order_by(Project.status.asc(), Project.created_at.desc()).all()
    return render_template('projects.html', projects=all_projects)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project-detail.html', project=project)

@app.route('/blogs')
def blogs():
    all_blogs = Blog.query.order_by(Blog.timestamp.desc()).all()
    return render_template('blogs.html', blogs=all_blogs)

@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return render_template('blog-detail.html', blog=blog)


# --- Admin Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            flash('Successfully logged in.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(50).all()
    messages = ContactMessage.query.order_by(ContactMessage.timestamp.desc()).all()
    projects = Project.query.all()
    members = TeamMember.query.all()
    blogs = Blog.query.order_by(Blog.timestamp.desc()).all()
    team_info = TeamInfo.query.first()
    return render_template('dashboard.html', logs=logs, messages=messages, projects=projects, members=members, blogs=blogs, team_info=team_info)

# --- Admin: Team Info ---
@app.route('/dashboard/team-info', methods=['POST'])
@login_required
def edit_team_info():
    info = TeamInfo.query.first()
    if not info:
        info = TeamInfo()
        db.session.add(info)
    info.mission = request.form.get('mission')
    info.what_we_do = request.form.get('what_we_do')
    info.why_we_do = request.form.get('why_we_do')
    db.session.commit()
    flash('Team Info updated successfully.', 'success')
    return redirect(url_for('dashboard'))

# --- Admin: Team Members ---
@app.route('/dashboard/member/new', methods=['GET', 'POST'])
@login_required
def new_member():
    if request.method == 'POST':
        new_m = TeamMember( # type: ignore
            name=request.form.get('name'),
            role=request.form.get('role'),
            short_bio=request.form.get('short_bio'),
            full_bio=request.form.get('full_bio'),
            contributions=request.form.get('contributions'),
            experience=request.form.get('experience'),
            github_link=request.form.get('github_link'),
            twitter_link=request.form.get('twitter_link'),
            image_url=request.form.get('image_url') or f"https://api.dicebear.com/7.x/avataaars/svg?seed={request.form.get('name')}"
        )
        db.session.add(new_m)
        db.session.commit()
        flash('Team member added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('member-edit.html', member=None)

@app.route('/dashboard/member/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_member(id):
    member = TeamMember.query.get_or_404(id)
    if request.method == 'POST':
        member.name = request.form.get('name')
        member.role = request.form.get('role')
        member.short_bio = request.form.get('short_bio')
        member.full_bio = request.form.get('full_bio')
        member.contributions = request.form.get('contributions')
        member.experience = request.form.get('experience')
        member.github_link = request.form.get('github_link')
        member.twitter_link = request.form.get('twitter_link')
        if request.form.get('image_url'):
            member.image_url = request.form.get('image_url')
        db.session.commit()
        flash('Team member updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('member-edit.html', member=member)

@app.route('/dashboard/member/<int:id>/delete', methods=['POST'])
@login_required
def delete_member(id):
    m = TeamMember.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    flash('Team member deleted.', 'info')
    return redirect(url_for('dashboard'))

# --- Admin: Blogs ---
@app.route('/dashboard/blog/new', methods=['GET', 'POST'])
@login_required
def new_blog():
    if request.method == 'POST':
        b = Blog( # type: ignore
            title=request.form.get('title'),
            content=request.form.get('content'),
            author=request.form.get('author'),
            tags=request.form.get('tags')
        )
        db.session.add(b)
        db.session.commit()
        flash('Blog post added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('blog-edit.html', blog=None)

@app.route('/dashboard/blog/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_blog(id):
    blog = Blog.query.get_or_404(id)
    if request.method == 'POST':
        blog.title = request.form.get('title')
        blog.content = request.form.get('content')
        blog.author = request.form.get('author')
        blog.tags = request.form.get('tags')
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('blog-edit.html', blog=blog)

@app.route('/dashboard/blog/<int:id>/delete', methods=['POST'])
@login_required
def delete_blog(id):
    b = Blog.query.get_or_404(id)
    db.session.delete(b)
    db.session.commit()
    flash('Blog post deleted.', 'info')
    return redirect(url_for('dashboard'))

# --- Admin: Projects (Existing) ---
@app.route('/dashboard/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        new_proj = Project( # type: ignore
            title=request.form.get('title'),
            short_description=request.form.get('short_description'),
            category=request.form.get('category'),
            status=request.form.get('status', 'Past'),
            tags=request.form.get('tags'),
            icon=request.form.get('icon', 'box'),
            overview=request.form.get('overview'),
            challenges=request.form.get('challenges'),
            modifications=request.form.get('modifications'),
            results=request.form.get('results'),
            timeline=request.form.get('timeline'),
            role=request.form.get('role'),
            technologies=request.form.get('technologies'),
            github_link=request.form.get('github_link')
        )
        db.session.add(new_proj)
        db.session.commit()
        flash('Project added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('project-edit.html', project=None)

@app.route('/dashboard/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.short_description = request.form.get('short_description')
        project.category = request.form.get('category')
        project.status = request.form.get('status', 'Past')
        project.tags = request.form.get('tags')
        project.icon = request.form.get('icon')
        project.overview = request.form.get('overview')
        project.challenges = request.form.get('challenges')
        project.modifications = request.form.get('modifications')
        project.results = request.form.get('results')
        project.timeline = request.form.get('timeline')
        project.role = request.form.get('role')
        project.technologies = request.form.get('technologies')
        project.github_link = request.form.get('github_link')
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('project-edit.html', project=project)

@app.route('/dashboard/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.', 'info')
    return redirect(url_for('dashboard'))

def init_db():
    with app.app_context():
        db.create_all()
        # Seed some data if empty
        if not TeamInfo.query.first():
            info = TeamInfo( # type: ignore
                mission="We build robust, intelligent systems. Bridging the gap between code and reality.",
                what_we_do="We are a collective of developers, engineers, and designers working on cutting-edge software and hardware integration.",
                why_we_do="Because standard solutions aren't good enough. We build things because we love to build."
            )
            db.session.add(info)
            db.session.commit()

if __name__ == '__main__':
    db_path = os.path.join(basedir, 'team_portfolio.db')
    if not os.path.exists(db_path):
        init_db()
    app.run(debug=True)

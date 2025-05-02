from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///incidents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Incident Model
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(10), nullable=False)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'reported_at': self.reported_at.isoformat() + 'Z'
        }

# Create the database and add sample data if empty
def initialize_database():
    with app.app_context():
        db.create_all()
        if not Incident.query.first():
            sample_incidents = [
                Incident(
                    title="Incident 1", 
                    description="Description 1", 
                    severity="High"
                ),
                Incident(
                    title="Incident 2", 
                    description="Description 2", 
                    severity="Medium"
                ),
                Incident(
                    title="Incident 3", 
                    description="Description 3", 
                    severity="Low"
                )
            ]
            db.session.bulk_save_objects(sample_incidents)
            db.session.commit()

# Validation function

def validate_incident(data):
    errors = []

    if not data.get('title', '').strip():
        errors.append("Title is required.")
    if not data.get('description', '').strip():
        errors.append("Description is required.")
    if data.get('severity') not in {"Low", "Medium", "High"}:
        errors.append("Severity must be one of: Low, Medium, High.")

    return errors

# Routes
@app.route('/incidents', methods=['GET'])
def get_incidents():
    incidents = Incident.query.all()
    return jsonify([i.to_dict() for i in incidents]), 200


@app.route('/incidents', methods=['POST'])
def create_incident():
    data = request.get_json()
    errors = validate_incident(data)

    if errors:
        return jsonify({"errors": errors}), 400

    incident = Incident(
        title=data['title'].strip(),
        description=data['description'].strip(),
        severity=data['severity']
    )
    db.session.add(incident)
    db.session.commit()

    return jsonify(incident.to_dict()), 201


@app.route('/incidents/<int:id>', methods=['GET'])
def get_incident(id):
    incident = Incident.query.get_or_404(id)
    return jsonify(incident.to_dict()), 200


@app.route('/incidents/<int:id>', methods=['DELETE'])
def delete_incident(id):
    incident = Incident.query.get_or_404(id)
    db.session.delete(incident)
    db.session.commit()
    return '', 204


if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)

from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import socket
import os

app = Flask(__name__)

# Expose automatiquement /metrics pour Prometheus
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application GitOps de Fadyl Axel BAMBA', version='1.0.0')

NOM_COMPLET = "Fadyl Axel BAMBA"
SLUG = "fadyl-axel-bamba"

@app.route("/")
def home():
    return jsonify({
        "message": f"Plateforme GitOps observable - {NOM_COMPLET}",
        "endpoint_personnalise": f"/{SLUG}",
        "hostname": socket.gethostname(),
        "version": os.environ.get("APP_VERSION", "1.0.0")
    })

@app.route(f"/{SLUG}")
def perso():
    return jsonify({
        "etudiant": NOM_COMPLET,
        "projet": "Plateforme GitOps observable sur Kubernetes",
        "hostname": socket.gethostname(),
        "version": os.environ.get("APP_VERSION", "1.0.0")
    })

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200

@app.route("/readyz")
def readyz():
    return jsonify({"status": "ready"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# Plateforme GitOps observable - Fadyl Axel BAMBA - M1 SSI

## 0. Structure du dépôt
```
app/                    -> code Flask + Dockerfile + tests
helm-chart/             -> chart Helm (namespace, deployment, service)
.github/workflows/ci.yml -> pipeline CI (test, lint, scan, push)
```

## 1. Créer le dépôt GitHub
1. Va sur github.com -> New repository -> nom: `fadyl-axel-bamba-app` -> Public
2. En local :
```bash
cd projet-gitops
git init
git add .
git commit -m "Initial commit - plateforme GitOps"
git branch -M main
git remote add origin https://github.com/TON_USER_GITHUB/fadyl-axel-bamba-app.git
git push -u origin main
```
3. **IMPORTANT** : édite `helm-chart/fadyl-axel-bamba-app/values.yaml` et remplace
   `TON_USER_GITHUB` par ton vrai identifiant GitHub, puis re-commit/push.

4. Vérifie que le package est bien public :
   GitHub -> ton profil -> Packages -> `fadyl-axel-bamba-app` -> Package settings
   -> Change visibility -> Public (sinon k3s ne pourra pas puller l'image sans secret).

## 2. Installer k3s sur le control plane (VM master)
```bash
curl -sfL https://get.k3s.io | sh -s - \
  --disable traefik --disable servicelb --disable metrics-server

# Récupérer le token pour les workers
sudo cat /var/lib/rancher/k3s/server/node-token
```

## 3. Joindre les 2 workers
Sur chaque VM worker (remplace IP_MASTER et TOKEN) :
```bash
curl -sfL https://get.k3s.io | K3S_URL=https://IP_MASTER:6443 \
  K3S_TOKEN=TOKEN sh -
```

## 4. Vérifier le cluster (depuis le master)
```bash
sudo kubectl get nodes -o wide
# tu dois voir 3 nœuds : 1 control-plane + 2 worker en état Ready
```

Astuce pour éviter `sudo` à chaque commande :
```bash
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config
export KUBECONFIG=~/.kube/config
```

## 5. Installer Helm (si pas déjà présent)
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

## 6. Installer Argo CD
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Récupérer le mot de passe admin initial
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d

# Exposer l'UI (en local, dans un terminal séparé)
kubectl port-forward svc/argocd-server -n argocd 8080:443
# -> https://localhost:8080  (user: admin)
```

## 7. Créer l'Application Argo CD (pointant vers ton repo)
```bash
kubectl apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: fadyl-axel-bamba-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/TON_USER_GITHUB/fadyl-axel-bamba-app.git
    targetRevision: main
    path: helm-chart/fadyl-axel-bamba-app
  destination:
    server: https://kubernetes.default.svc
    namespace: ns-fadyl-axel-bamba
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
EOF
```
Capture d'écran ici : l'UI Argo CD qui montre l'app "Synced/Healthy".

## 8. Installer la stack observabilité (Prometheus + Grafana)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set grafana.adminPassword=admin123 \
  --set prometheus.prometheusSpec.retention=2d \
  --set prometheus.prometheusSpec.resources.requests.memory=256Mi \
  --set grafana.resources.requests.memory=128Mi
```

Accéder à Grafana :
```bash
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
# -> http://localhost:3000  (admin / admin123)
```
Crée un dashboard nommé **"Dashboard - Fadyl Axel BAMBA"** avec au moins 1 panel
(ex: nombre de requêtes HTTP via la métrique exposée par prometheus-flask-exporter).

## 9. Installer Loki (logs) - version légère
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set loki.persistence.enabled=false \
  --set promtail.enabled=true
```
Ajoute Loki comme datasource dans Grafana (Configuration -> Data sources -> Loki
-> URL: `http://loki:3100`) puis montre les logs de ton app dans Grafana Explore.

## 10. Vérifier l'app et le rollback
```bash
kubectl get pods -n ns-fadyl-axel-bamba
kubectl port-forward svc/fadyl-axel-bamba-app -n ns-fadyl-axel-bamba 8000:80
curl http://localhost:8000/fadyl-axel-bamba

# Test de rollback Helm (via Argo CD ou en direct) :
helm history fadyl-axel-bamba-app -n ns-fadyl-axel-bamba
helm rollback fadyl-axel-bamba-app 1 -n ns-fadyl-axel-bamba
```

## 11. Traces (OpenTelemetry) - version minimale
Pour rester dans les temps, installe juste le collector et montre qu'il reçoit
des données (capture d'écran des logs du collector suffit pour le rapport) :
```bash
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm install otel-collector open-telemetry/opentelemetry-collector \
  --namespace monitoring \
  --set mode=deployment \
  --set config.exporters.logging.loglevel=debug
```

## Checklist personnalisation (obligatoire pour être noté)
- [ ] Endpoint `/fadyl-axel-bamba` répond avec le nom complet
- [ ] Namespace = `ns-fadyl-axel-bamba`
- [ ] Release Helm = `fadyl-axel-bamba-app`
- [ ] Dépôt Git nommé `fadyl-axel-bamba-app`
- [ ] Dashboard Grafana intitulé avec le nom complet
- [ ] Nom/prénom visible dans TOUTES les captures d'écran du rapport

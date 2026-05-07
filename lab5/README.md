# Добавляем репозиторий с чартами Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Устанавливаем ВЕСЬ стек мониторинга
helm install monitoring prometheus-community/kube-prometheus-stack

# Собираем образ внутри миникуба
minikube image build -t my-flask-app:3.0 .

# Деплоим приложение и ServiceMonitor
kubectl apply -f k8s/app.yaml

kubectl get pods

minikube service flask-svc

kubectl port-forward svc/monitoring-grafana 8080:80

http://localhost:8080

Логин: admin
Пароль:
kubectl get secrets -A
kubectl get secret monitoring-grafana -o jsonpath="{.data.admin-password}" # | base64 -d (linux)

flask_http_request_total

for /L %i in (1,1,100) do curl -s "http://127.0.0.1:48591/" >nul & curl -s "http://127.0.0.1:48591/error" >nul

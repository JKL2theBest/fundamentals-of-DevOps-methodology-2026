# 5 Лабораторная (Базовая) черновик

Выполнил:

студент группы N3346,

Суханкулиев Мухаммет

---

## Контекст

В качестве подопытного использовано микро-веб-приложение на Flask из прошлых лабораторных работ, доработанное для отдачи метрик в формате Prometheus.

---

### 1. Подготовка приложения

Чтобы Prometheus мог что-то собирать, приложение должно уметь отдавать метрики. Я добавил в код Flask библиотеку `prometheus-flask-exporter`.

Она автоматически оборачивает все маршруты и создает эндпоинт `/metrics`, где публикуются данные о количестве запросов, HTTP-кодах (200, 404, 500) и задержках (latency).

Ещё я специально добавил маршрут `/error` с ошибкой, чтобы можно было визуализировать на графиках всплески 500-х ошибок.

### 2. Установка стека мониторинга

Использовал Helm. Установил официальный стек `kube-prometheus-stack`, который включает в себя сразу всё необходимое "из коробки" (в том числе метрики самого кластера).

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

![prometheus-community](./screenshots/1.minikube_helm.png)

```bash
helm install monitoring prometheus-community/kube-prometheus-stack
```

![kube-prometheus-stack](./screenshots/2.helm_install.png)

### 3. ServiceMonitor

Чтобы Prometheus узнал о существовании моего приложения, я не стал править конфиги Прометеуса вручную (это антипаттерн). Вместо этого реализовал манифест `ServiceMonitor`. 

Это Custom Resource Definition (CRD), который динамически сообщает оператору Prometheus: *"Иди к подам с lable `app: flask-monitor` на порт 8000 и собирай метрики, чел"*.

# Собираем образ внутри миникуба

```bash
minikube image build -t my-flask-app:3.0 .
```

![CLI Setup](./screenshots/3.1.minikube_image_build.png)

# Деплоим приложение и ServiceMonitor

```bash
kubectl apply -f k8s/app.yaml
```

![CLI Setup](./screenshots/3.2.kubectl_apply.png)

```bash
kubectl get pods

minikube service flask-svc
```

![CLI Setup](./screenshots/4.pods_service.png)

```bash
kubectl port-forward svc/monitoring-grafana 8080:80
```

![CLI Setup](./screenshots/5.port-forward.png)

---

## Графаня

http://localhost:8080

Логин: admin
Пароль:

```bash
kubectl get secrets -A
```

```bash
kubectl get secret monitoring-grafana -o jsonpath="{.data.admin-password}" # | base64 -d (linux)
```

![CLI](./screenshots/6.1.nahojdenie_passworda.png)

![CLI](./screenshots/6.2.cyberchef.org.png)

![CLI](./screenshots/7.grafana_login.png)

(можно ли было задать пароль в начале? ...)

---

## Результаты (Графики Графани)

После деплоя я пробросил порт к Grafana (`kubectl port-forward svc/monitoring-grafana 8080:80`) и сгенерировал искусственную нагрузку на приложение:

```bash
for /L %i in (1,1,100) do curl -s "http://127.0.0.1:48591/" >nul & curl -s "http://127.0.0.1:48591/error" >nul
```

### График 1: Состояние системы (Инфраструктурный мониторинг)

`kube-prometheus-stack` автоматически создает дашборды для мониторинга железа и подов Kubernetes. Ниже представлен график ...

*Скриншот системных ...:*
![...](./screenshots/8.prometheus_overview.png)

### График 2: Состояние приложения (Продуктовый мониторинг)

Я создал кастомный Dashboard, чтобы отслеживать метрики конкретно моего приложения. 

PromQL запрос: `flask_http_request_total`. На графике наглядно видно распределение входящих запросов. Красная и синяя линии - это те самые 500-е ошибки, вызванные моими обращениями к маршруту `/error`, а зеленая и оранжевая - успешные запросы.......

![...](./screenshots/9.new_dashboard.png)

*Скриншот продуктовых метрик (Flask App):*
![App Metrics](./screenshots/10.flask_requests.png)

### фсё

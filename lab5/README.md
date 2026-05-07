# 5 Лабораторная (Мониторинг)

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

*Добавление репозитория:*

![prometheus-community](./screenshots/1.minikube_helm.png)

```bash
helm install monitoring prometheus-community/kube-prometheus-stack
```

*Установка стека:*

![kube-prometheus-stack](./screenshots/2.helm_install.png)

### 3. ServiceMonitor

Чтобы Prometheus узнал о существовании моего приложения, я не стал править конфиги Прометеуса вручную (это антипаттерн). Вместо этого реализовал манифест `ServiceMonitor`. 

Это Custom Resource Definition (CRD), который динамически сообщает оператору Prometheus: *"Иди к сервису с label `app: flask-monitor` и собирай метрики, чел"*.

### 4. Сборка и Деплой

Собираем образ внутри миникуба (чтобы k8s не пытался скачать его из интернета):

```bash
minikube image build -t my-flask-app:3.0 .
```

![Image Build](./screenshots/3.1.minikube_image_build.png)

Деплоим манифесты приложения:

```bash
kubectl apply -f k8s/app.yaml
```

![Kubectl Apply](./screenshots/3.2.kubectl_apply.png)

Проверяем поды и открываем туннель к приложению:

```bash
kubectl get pods
minikube service flask-svc
```

![Pods and Service](./screenshots/4.pods_service.png)

Прокидываем порт к Grafana на `localhost:8080`:

```bash
kubectl port-forward svc/monitoring-grafana 8080:80
```

![Port Forward](./screenshots/5.port-forward.png)

---

## Вход в Графиню

Панель Grafana доступна по адресу `http://localhost:8080`.

* Логин по умолчанию: `admin`
* Пароль генерируется автоматически при установке Helm-чарта.

*(Примечание: пароль можно было задать при установке через `--set grafana.adminPassword=...`, но уже было поздно...).*

Чтобы узнать пароль, я посмотрел секреты кластера и вытащил нужный в формате json:

```bash
kubectl get secrets -A
kubectl get secret monitoring-grafana -o jsonpath="{.data.admin-password}"
```

*Поиск секрета:*

![Secret Search](./screenshots/6.1.nahojdenie_passworda.png)

Так как стандартная консоль Windows не поддерживает линуксовую команду `base64 -d`, я скопировал закодированное значение и расшифровал его с помощью **CyberChef** (кибер-повар😁):

*Декодирование Base64 в CyberChef:*

![CyberChef](./screenshots/6.2.cyberchef.org.png)

*Окно входа в Графаню:*

![Grafana Login](./screenshots/7.grafana_login.png)

---

## Результаты (Графики Графани)

Для проверки мониторинга я сгенерировал нагрузку на приложение:

```cmd
for /L %i in (1,1,100) do curl -s "http://127.0.0.1:48591/" >nul & curl -s "http://127.0.0.1:48591/error" >nul
```

### График 1: Состояние системы (Инфраструктурный мониторинг)

`kube-prometheus-stack` автоматически создает дашборды для мониторинга железа и компонентов k8s. Ниже представлен стандартный график `Prometheus / Overview`, отражающий сбор метрик с таргетов.

*Скриншот системных метрик:*

![Prometheus Overview](./screenshots/8.prometheus_overview.png)

### График 2: Состояние приложения (Продуктовый мониторинг)

Я создал кастомный Dashboard, чтобы отслеживать метрики конкретно моего приложения. 

PromQL запрос: `flask_http_request_total`. На графике видно распределение входящих запросов. 

**Важный нюанс:** На графике видно 4 линии. Это произошло потому, что у нас работает **2 пода (реплики)**, и каждый из них отдает по **2 статуса** (200 OK и 500 Error). Nginx/Kubernetes балансирует нагрузку между подами, поэтому графики растут равномерно.

*Настройка кастомного запроса:*

![New Dashboard](./screenshots/9.new_dashboard.png)

*Скриншот продуктовых метрик (Flask App):*

![App Metrics](./screenshots/10.flask_requests.png)

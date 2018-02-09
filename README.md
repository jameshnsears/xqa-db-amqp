# xqa-db-rest [![Build Status](https://travis-ci.org/jameshnsears/xqa-db-rest.svg?branch=master)](https://travis-ci.org/jameshnsears/xqa-db-rest) [![Coverage Status](https://coveralls.io/repos/github/jameshnsears/xqa-db-rest/badge.svg?branch=master)](https://coveralls.io/github/jameshnsears/xqa-db-rest?branch=master)
* a REST to PostgresSQL interface.

## 1. High Level Design
![High Level Design](https://github.com/jameshnsears/xqa-documentation/blob/master/uml/rest-amqp-sequence-diagram.jpg)

## 2. Maven
### 2.1. Clean .m2
* rm -rf $HOME/.m2/*

### 2.2. Test - needs xqa-manager to be running!
* mvn clean compile test
* mvn jacoco:report coveralls:report
* mvn site  # findbugs

### 2.3. Package
* mvn package -DskipTests

### 2.4. Run
* java -jar target/xqa-db-rest-1.0.0-SNAPSHOT.jar server xqa-db-rest.yml

#### 2.4.1. Endpoints
* curl http://127.0.0.1:8080/search/correlationId/2
* curl http://127.0.0.1:8080/status
* curl http://127.0.0.1:8080/xquery -X POST -H "Content-Type: application/json" -d '{"xqueryRequest":"//", "content": "ppp"}'

#### 2.4.2. Builtin Admin Tasks
* curl -X POST http://127.0.0.1:8081/tasks/log-level -H "Content-Type: application/json" -d "logger=ROOT&level=DEBUG"
* curl -X POST http://127.0.0.1:8081/tasks/gc
* curl http://127.0.0.1:8081/healthcheck

#### 2.4.3. Metrics
* curl http://127.0.0.1:8081/metrics

## 3. Docker
### 3.1. Build locally
* docker-compose -p "dev" build --force-rm

or

* mvn clean install dockerfile:build

### 3.2. Bring up
* docker run -d --net="host" --name="xqa-db-rest" xqa-db-rest

or

* docker-compose -p "dev" up -d

### 3.3. Teardown
* docker-compose -p "dev" down --rmi all -v

## 4. Banner
[taag](http://patorjk.com/software/taag/#p=display&f=Standard&t=xqa-db-rest)

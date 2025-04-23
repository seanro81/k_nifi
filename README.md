Отчет Задание 5  Kafka в production и интеграция Kafka с Big Data экосистемой
================================================================================================================
  - Задание 1.Развёртывание и настройка Kafka-кластера в Yandex Cloud

    - параметры кластера - Kaka 3 ноды по 2 vCPU, 8 ГБ RAM  32 ГБ network-ssd (в одном сетевом сегменте)
                      - Zookeper  3 ноды по 2 vCPU,8 ГБ RAM  10 ГБ network-ssd (каждая нода в своем сегменте сети)
    - 
                      \screens\kafka_cluster_config.png  - настройки кластера
                      \screens\data_topic_config.png     - настройки топика data_topic
                      \app\message-01.json               - json схема
    -                 \app\consumer_schema.py            - консумер настроенный на schema_registry
                      \app\producer_schema.py            - продюсер настроенный на schema_registry
                      \screens\результат_curl_schema.png - результат вызова curl http://localhost:8081/subjects
                                                           и curl -X GET http://localhost:8081/subjects/data_topic-value/versions
                      \screens\результат_describe.png    - результат вызова kafka-topics.bat --describe
                    
                       C:\kafka\bin\windows\kafka-topics.bat --describe --bootstrap-server rc1d-9a231tu2d3r1fgdv.mdb.yandexcloud.net:9091 --command-config config.properties
             Topic: data_topic       TopicId: 4b42FJTcS6Gt4jsXKA4yIg PartitionCount: 3       ReplicationFactor: 3    Configs: min.insync.replicas=2,cleanup.policy=delete,segment.bytes=104857600,retention.ms=86400000
             Topic: data_topic       Partition: 0    Leader: 1       Replicas: 1,2,3 Isr: 1,2,3      Elr: N/A        LastKnownElr: N/A
             Topic: data_topic       Partition: 1    Leader: 2       Replicas: 2,3,1 Isr: 2,3,1      Elr: N/A        LastKnownElr: N/A
             Topic: data_topic       Partition: 2    Leader: 3       Replicas: 3,1,2 Isr: 3,1,2      Elr: N/A        LastKnownElr: N/A
         
             лог  отправки сообщений
            (venv) C:\Users\Andre\Desktop\Архитектура\KAFKA_COURSE\DZ_5_kafka\app>python producer_schema.py
            Registered schema for data_topic-value with id: 1
            Delivered message to topic data_topic [2] at offset 1

            лог прием сообщений
           (venv) C:\Users\Andre\Desktop\Архитектура\KAFKA_COURSE\DZ_5_kafka\app>python consumer_schema.py
           Message on data_topic:
           {'id': 1, 'from': 'demo_user', 'to': 'user_113', 'msg': 'hello'}
            Closing consumer
         
            создание truststore 
                 keytool.exe -importcert -alias YandexCA  --file yandex_ca.crt --keystore truststore  --storepass test123 --noprompt
 
           Настройка   Confluent Schema Registry
           ====================================================================================================
                  !!! Настраивается на VM Yandex Cloud !!!!
                  !!! параметры  CPU Intel Ice Lake	2	 MEM2 ГБ	SSD	18 ГБ	ru-central1-d !!!
                  
                   Создайте топик для уведомлений об изменении схем форматов данных schemas
                   Создайте служебный топик с именем schemas со следующими настройками:

                   Количество разделов — 1.
                   Политика очистки лога — Compact.
	 
                   пользователь на  schemas
	                       user registry
	                       password ******
    

                   Установите и настройте Confluent Schema Registry на виртуальной машине
	                 Подключите репозиторий Confluent Schema Registry:
		              wget -qO - https://packages.confluent.io/deb/6.2/archive.key | sudo apt-key add - && \
                      sudo add-apt-repository "deb [arch=amd64] https://packages.confluent.io/deb/6.2 stable main"
		  
                   Установите пакеты:
	                sudo apt-get update && \
                    sudo apt-get install \
                    confluent-schema-registry \
                    openjdk-11-jre-headless \
                    python3-pip --yes
	 
	               Создать сертификат CA
	                sudo mkdir /opt/ca-cert/
	 
                    sudo wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
                    --output-document /opt/ca-cert/YandexInternalRootCA.crt 
	 
                    sudo chmod 0655 /opt/ca-cert/YandexInternalRootCA.crt

                    Сертификат будет сохранен в файле /opt/ca-cert/YandexInternalRootCA.crt
                    Создайте для сертификата защищенное хранилище:
	                  sudo keytool \
                         -keystore /etc/schema-registry/client.truststore.jks \
                         -alias CARoot \
                         -import -file /opt/ca-cert/YandexInternalRootCA.crt \
                         -storepass test123 \
                         --noprompt
	 
	               Создайте файл /etc/schema-registry/jaas.conf с настройками для подключения к кластеру:
	
                 KafkaClient {
                    org.apache.kafka.common.security.scram.ScramLoginModule required
                    username="*******"
                    password="********";
                  };
                    
                  Измените файл /etc/schema-registry/schema-registry.properties, отвечающий за настройки Confluent Schema Registry:
                      Закомментируйте строку: kafkastore.bootstrap.servers=PLAINTEXT://localhost:9092
                      изменить параметр kafkastore.topic=schemas
                
                 Добавьте в конец файла строки:

                    kafkastore.bootstrap.servers=SASL_SSL://rc1d-9a231tu2d3r1fgdv.mdb.yandexcloud.net:9091,rc1d-b2oto009a86oslfg.mdb.yandexcloud.net:9091,rc1d-pbv9db5m2h8uf9gq.mdb.yandexcloud.net:9091
                    kafkastore.ssl.truststore.location=/etc/schema-registry/client.truststore.jks
                    kafkastore.ssl.truststore.password=test123
                    kafkastore.sasl.mechanism=SCRAM-SHA-512
                    kafkastore.security.protocol=SASL_SSL

                   Измените файл с описанием модуля systemd /lib/systemd/system/confluent-schema-registry.service.

                   Перейдите в блок [Service].

                  Добавьте параметр Environment с настройками Java:

                  [Service]
                  Type=simple
                  User=cp-schema-registry
                  Group=confluent
                  Environment="LOG_DIR=/var/log/confluent/schema-registry"
                  Environment="_JAVA_OPTIONS='-Djava.security.auth.login.config=/etc/schema-registry/jaas.conf'"

                 Обновите сведения о модулях systemd: sudo systemctl daemon-reload

                  Запустите сервис Confluent Schema Registry:  sudo systemctl start confluent-schema-registry.service

                   автоматический запуск Confluent Schema Registry после перезагрузки ОС: sudo systemctl enable confluent-schema-registry.service
                   
      
 

Задание 2 итеграция Apache NIFI с Kafka cluster (Yandex Cloud)
==================================================================================================================
                      \nifi_data\input.json              - входной файл содержащий json 
                      
                      \screens\nifi_kafka_cloud.png      - Скрин ETL процесса - 
                                                              GetFile - чтение файлов 
                                                              PublishKafkaRecord - запись в Yandex cloud Kafka 
                      а также скрин консоли проверки чтения из Кафка  kafka-console-consumer.bat
                       kafka-console-consumer.bat --bootstrap-server rc1d-9a231tu2d3r1fgdv.mdb.yandexcloud.net:9091 --topic data_topic --property print.key=true --property key.separator=":"  --consumer-property security.protocol=SASL_SSL --consumer-property sasl.mechanism=SCRAM-SHA-512 --consumer-property ssl.truststore.location=truststore --consumer-property ssl.truststore.password=test123 --consumer-property sasl.jaas.config="org.apache.kafka.common.security.scram.ScramLoginModule required username='*****' password='*****';"
   

                      \screens\nifi_publishkafkarecord_config_1.png     - настройка PublishKafkaRecord
                      \screens\nifi_publishkafkarecord_config_2.png
                     
      
         

    



   
            
    
     
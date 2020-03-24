---
layout: post
comments: true
title: MySQL 이중화 대응 with ShardingSphere
category: [ Lab ]
---

### 문제발생
* 많은 양의 데이터가 수집되며, 동시에 읽고 쓰고 업데이트하는 과정이 발생함에 따라 MySQL 서버에 부하가 발생되며 성능이 저하가 됌  
* MySQL Replication을 이용하여 DBMS 단방향 이중화(Master/Slave)를 진행  
* Java로 구현된 모듈에서도 MySQL Replication에 대응하기 위한 로직 추가가 필요  

### ShardingSphere 오픈소스 발견 
* Spring Framework를 사용하지 않으면 DML 종류에 따라 Master/Slave 를 분기하는 귀찮은 로직을 개발해야 함  
* Google 검색 중 ShardingSphere 라는 오픈소스를 발견  
* <https://shardingsphere.apache.org>      
![_config.yml]({{ site.baseurl }}/assets/lab/2019-03-08/2019-03-08_shardingsphere_main.png)  
* ShardingSphere의 대표적인 기능으로 Read-Write Splitting 확인하여 사용하기로 결정  
![_config.yml]({{ site.baseurl }}/assets/lab/2019-03-08/2019-03-08_data_sharding_main.png)  


### ShardingSphere Read-Write Splitting Core 분석
* Master DB는 _**Only Single**_ 구성되며, Insert, Update, Delete 용도로 사용된다.
* Slave DB는 _**Multiple Slave**_ 여러개의 DB로 구성될 수 있으며, Select 용도로 사용된다.
* Slave DB는 내부 로드밸런스가 존재하여 적절하게 분배한다.
* 여러대의 Slave DB에서 Traffic 분산 가중치를 다르게 하고 싶다면 Config 설정을 통해 할 수도 있다.

### Sample Code 분석
#### Maven 설정
~~~
<dependency>
    <groupId>io.shardingsphere</groupId>
    <artifactId>sharding-jdbc-core</artifactId>
    <version>3.0.0</version>
</dependency>
~~~
버전은 크게 3가지 종류로 나뉘어진다. (2.x, 3.x, 4,x)  
* 2.x는 Legacy 버전이라 사용하지 않음  
* 3.x 버전은 활성화된 버전이며 3.0.0, 3.1.0 버전이 존재. 여기는 3.0.0 버전사용 (3.1.0 버전사용시 홈페이지에 있는 예제와 인자 값들이 안맞는 메소드들이 존재)  
* 4.x 개발 예정  
<https://mvnrepository.com/artifact/io.shardingsphere/sharding-jdbc>
![_config.yml]({{ site.baseurl }}/assets/lab/2019-03-08/2019-03-08_maven.png)

#### Java 코드
여기서는 Spring Framework를 사용하지 않았지만 공식 홈페이지에서는 Spring Framework를 위한 샘플 코드도 있다.    
아래는 Sample 코드(홈페이지에 있는 Sample 코드와는 조금 다름)를 보면,  
1. Master와, Slave1, Slave2로 구성되어 있으며 각 접속정보를 구성한다.
2. Slave DB는 여러개로 구성될 수 있어 Array 형식으로 입력받는다.
3. DataSource를 MasterSlaveDataSourceFactory 클래스의 Factory 패턴으로 DataSource를 입력받는다.
4. 마지막 인자 값 2개(HashMap, Properties)는 여기서는 지정할 필요가 없으므로 생성자만 던진다.
5. Insert, Update, Delete 쿼리는 Master DB로 연결되며, Select 쿼리는 Slave 쿼리로 알아서 연결된다.  
~~~
    // Configure actual data sources
    Map<String, DataSource> dataSourceMap = new HashMap<>();
    
    // Configure master data source
    BasicDataSource master = new BasicDataSource();
    masterDataSource.setDriverClassName("com.mysql.jdbc.Driver");
    masterDataSource.setUrl("jdbc:mysql://localhost:3306/ds_master");
    masterDataSource.setUsername("root");
    masterDataSource.setPassword("");
    dataSourceMap.put("master", master);
    
    // Configure first slave data source
    BasicDataSource slave0 = new BasicDataSource();
    slaveDataSource1.setDriverClassName("com.mysql.jdbc.Driver");
    slaveDataSource1.setUrl("jdbc:mysql://localhost:3306/ds_slave0");
    slaveDataSource1.setUsername("root");
    slaveDataSource1.setPassword("");
    dataSourceMap.put("slave0", slave0);
    
    // Configure second slave data source
    BasicDataSource slave1 = new BasicDataSource();
    slaveDataSource2.setDriverClassName("com.mysql.jdbc.Driver");
    slaveDataSource2.setUrl("jdbc:mysql://localhost:3306/ds_slave1");
    slaveDataSource2.setUsername("root");
    slaveDataSource2.setPassword("");
    dataSourceMap.put("slave1", slave1);
    
    // Configure read-write splitting rule
    MasterSlaveRuleConfiguration config = new MasterSlaveRuleConfiguration("master_slave", "master", Arrays.asList("slave0", "slave1"));
    
    // Get data source
    DataSource dataSource = MasterSlaveDataSourceFactory.createDataSource(dataSourceMap, config, new HashMap<>(), new Properties()));
~~~

### 결과 화면
CloudSQL을 사용하는 AppEngine 모듈에 적용해보았다.
![_config.yml]({{ site.baseurl }}/assets/lab/2019-03-08/2019-03-08_sql.png)
적용한 시점 부터 새로 구성된 Slave 인스턴스에 Connection이 생성된 것으로 확인된다.


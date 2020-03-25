---
layout: post
comments: true
title: 직렬화(Serialization)
category: [ Lab ]
---

### Serialization and Deserialization
* Serialization(직렬화): Object 혹은 Data를 외부 자바시스템에서도 사용할 수 있도록 Byte 형태로 변환  
* Deserialization(역직렬화): Byte 형태로 변환된 Data를 원래대로 Object 혹은 Data로 변환
* SerialVersionUID: 직렬화를 하면 내부에서 자동으로 SerialVersionUID 라는 고유의 번호를 생성하여 관리한다.    
이 UID는 직렬화와 역직렬화 할 때 체크포인트로 사용된다. 읽은 바이트 스트림이 어떤 클래스에 매핑되어 인스턴스화 되어야 할지 알아야 한다. 이 때, SerializationUID 도 함께 바이트스트림으로 저장되기 때문에 이를 먼저 읽은 후,
정확한 클래스를 찾을 수 있다. 즉, Type Safely 할 수 있다.

### 직렬화를 쓰는 이유
_**메모리 상에 존재하는 데이터**_ 를 _**파일로 저장하거나 외부로 전송**_ 할 때 고민으로 나온 것이다.  
주로 네트워크를 통해서 시스템간의 데이터 교환을 위해서 직렬화를 사용되며, 해당 데이터를 메모리에서만 관리한다면 객체 직렬화를 할 필요가 없다.    
  
프로세스 간에 데이터 전송에도 직렬화가 사용되는 이유는 대부분의 _**OS가 현재 가상메모리를 운영 중이며 대부분의 OS 의 프로세스 구현은 
서로 다른 가상메모리 주소공간(Virtual Address Space, VAS)를 갖기 때문에**_ 역시 마찬가지로 오브젝트 타입의 참조 값(결국 주소값) 데이터 인스턴스를 직접 줄 수 없어서
직렬화된 데이터로의 교환을 주로 사용한다. 

### JAVA 직렬화 방법 1
자바 기본(Primitive) 타입과 java.io.Serialization 인터페이스를 상속받은 객체는 직렬화 할 수 있는 기본 조건을 갖는다.

### JAVA 직렬화 방법 2
자바의 Serialization 을 사용하지 않더라도 정보를 대상 시스템에 복원가능하게 전달하기 위해서 아래와 같은 형태로 변경 할 수도 있다.
* CSV
* JSON
* XML

![_config.yml]({{ site.baseurl }}/assets/lab/2020-01-15/2020-01-15_serialization.png)

### 직렬화의 최적화
데이터 변환 및 전송 속도에 최적화하여 별도의 직렬화 방법을 제시하는 구조이다.    

### 직렬화 FrameWork
* Avro: Apache Hadoop 프로젝트에서 개발된 RPC 및 데이터 직렬화 프레임워크이다. 
자료형과 프로토콜 정의를 위해 JSON을 사용하며 콤팩트 바이너리 포맷으로 데이터를 직렬화한다.   
주 사용 용도는 Hadoop에서 클라이언트 -> Hadoop Service 에 대해 영구 데이터를 위한 직렬화 포맷과 하둡 노드 간 통신을 위한 와이어 포맷을 둘 다 제공한다.  
Thrift나 Protocol Buffer와 비슷하지만 스키마 변경이 발생할 때 코드 생성 프로그램의 실행을 요구하지 않는다.
* Protocol Buffer: 구조화된 데이터를 직렬화하는 방식이다. 유선이나 데이터 저장을 목적으로 서로 통신할 프로그램을 개발할 때 유용하다.
* Thrift: RPC 프레임워크를 형성하며 페이스북에서 "스케일링 가능한 언어 간 서비스 개발"을 위해 개발되었다. 현재는 아파치에서 관리되고 있다.
    
*직렬화 Framework에 대한 각각의 상세한 설명은 다음포스팅에...*


### 참조  
<http://woowabros.github.io/experience/2017/10/17/java-serialize.html>

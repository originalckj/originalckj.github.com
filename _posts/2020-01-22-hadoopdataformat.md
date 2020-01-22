---
layout: post
comments: true
title: Hadoop Data Format History
category: [ hadoop ]
---

### Hadoop 저장 포맷
원래 Hadoop의 HDFS는 Text File 형태로 저장된다. Text File 포맷은 데이터 저장공간과 처리속도면에서 문제가 발생하면서 효율적인 처리방식을
고민하게 되었다. 빅데이터의 처리는 많은 시간과 비용이 들어가므로 _**압축률을 높이거나 데이터를 효율적으로 관리**_ 하는게 핵심이다.     
이런 조건을 모두 만족할 수 있는건 Text File 포맷이 아닌 컬럼 기반의 데이터 포맷이다.    
컬럼 기반 포맷은 같은 종류의 데이터가 모여있으므로 압축률이 높고, 일부 컬럼만 읽어 들일 수 있어 처리량을 줄일 수 있다.

Hadoop 플랫폼에서 속도와 효율성을 높이기 위한 컬럼 기반의 대표 저장 포맷
* RC File (Row Columnar)
* ORC File (Optimized Row Columnar)
* Parquet

#### 저장 포맷 압축률 비교
![_config.yml]({{ site.baseurl }}/assets/2020-01-22/2020-01-22_compress.png)

### Hadoop 저장 포맷 History
![_config.yml]({{ site.baseurl }}/assets/2020-01-22/2020-01-22_history.png)
 
조회, 분석하는 Hive에서 컬럼스토어와 유사하게 구현하기 위한 RC File 이란 포맷이 맨 처음 페이스북에서 개발되었다.
컬럼 기반의 데이터 포맷 RC File을 사용함으로 써 Text File 포맷보다 압축률을 높이며 데이터를 효율적으로 관리 할 수 있게 되었지만,
아래와 같은 단점을 갖고 있다. 

* HDFS에 저장된 RC File들은 각 데이터노드에 흩어져 저장되므로 DB 테이블을 조회할 경우 각 노드에 분산된 파일을 모으는 작업을 거치게된다.
이 단계는 네트워크 비용을 증가시킬 뿐만 아니라 전체 성능을 느리게 한다.

RC File의 단점을 해결하기 위해 GFS 논문을 참고해 HDFS를 만들었던 더그 커팅이 트레비니(Trevini) 포맷을 제안 하지만 
트레비니는 RC 파일의 한계를 극복하기엔 단점이 많다는 지적을 받았다.

그러던 중 Hive 주요 공헌자였던 오웬 오말리 호튼웍스 부사장이 ORC File 포맷을 제안한다.
ORC File 특징은
* RC file 처럼 컬럼단위로 기록하되, 인덱스도 함께 기록 -> Read 과정에서 성능 향상
* 하나의 파일에 컬럼을 JSON 처럼 Nested 구조로 집어넣을 수 있다. -> 네임노드 부하 줄여줌
* Datetime, Decimal, Complex Type(List, Map, Struct, Union)의 Hive 타입 지원
* 높은 압축률과 데이터 모델의 우수성을 갖는다. -> 데이터 타입 기반의 압축(Integer: run-length encoding, String: Dictionary encoding)
* 파일 읽기 쓰기에 일정한 메모리 용량만 필요
* 다만 Hive에서만 가능하고 Java만 지원해 다양한 플랫폼에 적용하기 힘들다. -> 지금은 Hive 뿐만 아니라 다른 프로젝트에서도 사용가능

이 후, 더그 커팅은 오웬 오말리와 함께 트레비니와 ORC File의 공존을 모색을 제안했다.
하지만 더그 커팅의 클라우데라와 오웬 오말리의 호튼웍스는 경쟁 관계 이므로 오웬 오말리가 거절한다.
트레비니는 avro 란 오픈소스 프로젝트의 파일 포맷으로 발전

이런 가운데서 트위터가 Parquet라는 파일 포맷을 오픈소스에 제공
트위터 자신들의 서비스 속도를 높이기 위해 하둡을 위한 컬럼 스토어 포맷이 필요해 Parquet를 직접 개발
Parquet 특징은
* 하이브 뿐만 아니라 피그 같은 다양한 플랫폼에서 독립적으로 사용할 수 있도록
* JAVA 뿐만 아니라 C++도 지원 
* 구글 Dremel 논문을 참고해 만들어졌으며 ORC 파일처럼 Nested 구조로 컬럼을 하나의 파일안에 저장한다.
* 게시판에 댓글 달 듯 컬럼을 계층적 구조로 늘려가는 것
* 각 컬럼 값 마다 Repeated, Optional, Required 등의 구문을 넣을 수 있다.
* 여러 칼럼 테이블을 하나의 파일안에 집어 넣음으로써 조인 작업을 최소화
* 인코딩 방식도 다양해 데이터 모델 표현력이 좋다.

클라우데라가 Parquet를 적극적으로 지원하며, SQL on Hadoop 기술인 임팔라에 Parquet를 채택한다.

참조  
<http://www.zdnet.co.kr/view/?no=20131211140045>

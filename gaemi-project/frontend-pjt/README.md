# 🐜 gAemI Frontend

**gAemI** 프로젝트의 프론트엔드는 **Vue 3 기반 SPA(Single Page Application)**로, 실시간 주식 시세, 사용자 알림, AI 분석 결과를 사용자 친화적인 UI로 제공합니다.

단순한 화면 구현을 넘어, 백엔드에서 정의한 **REST API 및 WebSocket 통신 구조를 UI 계층에서 명확히 해석하고 표현**하는 것을 목표로 합니다.

## 🎯 핵심 철학 (Core Philosophy)
본 프로젝트는 개발 과정에서 얻은 다음과 같은 기술적 통찰을 바탕으로 설계되었습니다.

1. **데이터 흐름의 해석과 연결**
   프론트엔드는 데이터의 관계나 비즈니스 로직의 구조를 독단적으로 결정하기보단, 백엔드가 설계한 데이터 흐름(Contract)을 UI 상에서 사용자 경험에 맞게 해석하고 연결하는 역할임을 이해하고 구현했습니다.

2. **실시간 렌더링과 UX 최적화**
   기능이 '작동'하는 것과 사용자가 '편안한' 것은 별개임을 배웠습니다. 실시간 데이터가 쏟아질 때 이를 그대로 화면에 뿌리기보다, **사용자가 정보를 안정적으로 인식할 수 있는 속도와 형태로 가공해 렌더링하는 것**이 UX의 핵심이라 판단하여 최적화 전략을 적용했습니다.

---

## 🧱 기술 스택 (Tech Stack)

| Category | Technology |
| --- | --- |
| **Framework** | Vue 3 (Composition API) |
| **Build Tool** | Vite |
| **State Management** | Pinia |
| **Routing** | Vue Router |
| **HTTP Client** | Axios |
| **Real-time** | WebSocket |
| **Styling** | CSS / Scoped SCSS |

---

## 📁 디렉토리 구조 (Directory Structure)

```bash
frontend-pjt/
├── public/                     # 정적 파일
├── src/
│   ├── api/                    # REST API 호출 로직 (Axios 인스턴스)
│   ├── services/               # WebSocket 핸들러 및 비즈니스 로직
│   ├── stores/                 # Pinia 전역 상태 (Global State)
│   ├── router/                 # 라우팅 설정 (Navigation Guard)
│   ├── components/             # 재사용 가능한 UI 컴포넌트
│   │   ├── alerts/             # 실시간 알림 UI
│   │   ├── chat/               # 챗봇 UI
│   │   ├── common/             # 버튼, 모달, 로딩 등 아토믹 컴포넌트
│   │   ├── dashboard/          # 대시보드 위젯 및 차트
│   │   ├── layout/             # Header, Sidebar 등 레이아웃
│   │   └── toast/              # 토스트 메시지 UI
│   ├── pages/                  # 라우터와 1:1 매핑되는 페이지
│   ├── views/                  # 여러 컴포넌트가 조합된 화면 뷰
│   ├── assets/                 # 이미지, 폰트 등 리소스
│   ├── data/                   # 상수(Constants), 목업 데이터
│   ├── App.vue                 # Root Component
│   └── main.js                 # Entry Point
├── index.html                  # HTML 진입점
├── package.json                # 의존성 및 스크립트
├── vite.config.js              # Vite 설정
└── Dockerfile                  # 배포용 Docker 설정
```
---
## 🔐 인증 및 상태 관리 (Auth & State)
**로그인 상태는 Pinia Store에서 전역으로 관리**되며, 프론트엔드는 오직 **"인증 상태에 따른 UI 접근 제어"** 역할만 수행합니다.
  - **Access Token 기반**: API 호출 시 헤더에 토큰을 포함하여 요청합니다.
  - **역할 분리**: 권한 검증 및 보안 정책 판단은 전적으로 백엔드에 위임합니다.
  - **활용 범위**: 화면 라우팅 가드(Guard), 보호된 API 호출, 사용자별 데이터 필터링.
---
## 🔄 데이터 통신 전략 (Data Strategy)
프론트엔드는 데이터의 성격에 따라 통신 방식과 UI 반영 방식을 엄격히 구분합니다.
**1. REST API (State)**
- **목적**: 화면 진입 시 필요한 **기준 상태(Baseline State)** 로딩.
- **대상**: 사용자 프로필, 관심 종목 리스트, 과거 차트 데이터 등.
- **처리**: 비동기 요청 후 Store에 상태로 저장하여 관리.

**2. WebSocket (Event)**
- **목적**: 휘발성 **실시간 이벤트(Real-time Event)** 수신.
- **대상**: 실시간 주가 변동, 체결 알림, 시스템 메시지.
- **처리**:
  - 모든 데이터를 Store에 저장하지 않음 (메모리 최적화). 
  - 이벤트 성격에 따라 토스트 메시지로 띄우거나, 필요한 경우에만 부분적으로 상태를 업데이트(Throttling 적용).
---
## ▶️ 실행 방법 (Getting Started)
별도의 환경 변수 설정 없이, 기본적으로 로컬 백엔드 서버와 통신하도록 설정되어 있습니다.

**1. 의존성 설치**
```bash
npm install
```
**2. 개발 서버 실행**
```bash
npm run dev
```
- **Frontend**: `http://localhost:5173`
- **Backend**: 기본적으로 `http://localhost:8080`을 바라보도록 설정되어 있습니다.
  - 만약 백엔드 포트가 다르다면 `src/api` 또는 `src/services` 내부의 설정 코드를 확인해 주세요.
- **⚠️ 주의**: 정상적인 데이터 로딩을 위해 백엔드 서버 및 WebSocket 서버가 실행 중이어야 합니다.
---
## 🐳 Docker 실행 (선택)
프로젝트 루트에 `docker-compose.yml`이 설정되어 있다면 아래 명령어로 실행할 수 있습니다.
```bash
docker-compose up -d --build
```
---
## 📌 참고 사항
- 본 프로젝트는 **백엔드 API 명세(Swagger)** 를 준수하여 구현되었습니다.
- 일부 UI 기능은 백엔드 API 제공 여부에 따라 비활성화될 수 있습니다.
- **상세한 기술적 의사결정 및 기술 문서(Notion) 링크는 프로젝트 최상위(Root) 경로의 README.md를 참고해 주세요.**
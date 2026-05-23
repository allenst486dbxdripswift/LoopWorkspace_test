# Fastlane Match 설정 가이드

이 문서는 Loop 프로젝트에 Fastlane `match`를 사용하여 코드 서명 인증서와 프로비저닝 프로파일을 관리하는 방법을 설명합니다.

## 1. 사전 요구사항
- Apple Developer 계정 액세스 권한
- App Store Connect API 키 (`FASTLANE_KEY_ID`, `FASTLANE_ISSUER_ID`, `FASTLANE_KEY`)
- GitHub 레포지토리(`Match-Secrets`)에 대한 쓰기 권한 및 Personal Access Token(`GH_PAT`)
- `fastlane`이 설치된 macOS 환경 (CI 환경에서도 동일하게 설정)

## 2. Match 레포지토리 초기화
```bash
# 레포지토리 URL 예시
MATCH_REPO="git@github.com:<YOUR_ORG>/Match-Secrets.git"

# 로컬에 클론 (CI에서는 자동으로 clone 하지 않음)
git clone $MATCH_REPO match_repo
cd match_repo

# fastlane match 초기화 (앱스토어 배포용)
fastlane match init appstore
```
위 명령을 실행하면 인증서와 프로비저닝 파일을 저장할 디렉터리가 생성됩니다.

## 3. CI 환경 변수 설정 (GitHub Actions)
```yaml
env:
  TEAMID: ${{ secrets.TEAMID }}
  GH_PAT: ${{ secrets.GH_PAT }}
  FASTLANE_KEY_ID: ${{ secrets.FASTLANE_KEY_ID }}
  FASTLANE_ISSUER_ID: ${{ secrets.FASTLANE_ISSUER_ID }}
  FASTLANE_KEY: ${{ secrets.FASTLANE_KEY }}
  GITHUB_REPOSITORY_OWNER: ${{ github.repository_owner }}
```
- `GH_PAT`은 `repo` 권한을 가진 Personal Access Token이어야 합니다.
- `FASTLANE_KEY`는 Base64 인코딩이 **되지 않은** PEM 형식의 키 내용이어야 합니다.

## 4. Fastlane `match` 호출 예시 (Fastfile에 정의)
```ruby
lane :certs do
  ENV["MATCH_READONLY"] = false.to_s
  match(
    type: "appstore",
    git_basic_authorization: Base64.strict_encode64("#{GITHUB_REPOSITORY_OWNER}:#{GH_PAT}"),
    app_identifier: [
      "com.#{TEAMID}.loopkit.appB.Loop",
      "com.#{TEAMID}.loopkit.appB.Loop.statuswidget",
      "com.#{TEAMID}.loopkit.appB.Loop.LoopWatch.watchkitextension",
      "com.#{TEAMID}.loopkit.appB.Loop.LoopWatch",
      "com.#{TEAMID}.loopkit.appB.Loop.Loop-Intent-Extension",
      "com.#{TEAMID}.loopkit.appB.Loop.LoopWidgetExtension"
    ]
  )
end
```
`match`가 성공하면 임시 키체인에 인증서와 프로비저닝 파일이 자동으로 import 됩니다.

## 5. 인증서가 없거나 만료된 경우 자동 재생성
Fastlane `match`는 기존 인증서가 없으면 자동으로 새 인증서를 생성합니다. CI에서 `MATCH_READONLY`를 `false` 로 설정하고 `lane :certs` 를 실행하면 됩니다.

## 6. 문제 해결 팁
- **No local code signing identities found**: `match` 실행 전 `MATCH_READONLY` 가 `false`인지, `GH_PAT` 가 올바른지 확인합니다.
- **키체인 충돌**: CI마다 새로운 키체인을 생성하도록 `setup_ci` 를 호출합니다 (`fastlane/actions/setup_ci`).
- **프로비저닝 프로파일 매핑 실패**: `update_code_signing_settings` 에서 `mapping["com.#{TEAMID}.loopkit.appB.Loop"]` 값이 `nil`이면 `match`가 올바르게 실행되지 않은 것입니다.

위 가이드를 프로젝트 루트에 `fastlane/MatchSetup.md` 로 커밋하고, CI 파이프라인에서 `lane :certs` 를 호출하면 코드 서명 문제가 해결됩니다.

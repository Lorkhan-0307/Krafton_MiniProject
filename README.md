# Krafton_MiniProject
This is Repository for Krafton week 0 mini project


-----
@app.route('/wiki/show', methods=['GET']) => 각 테마 별로 날짜,좋아요 순으로 도큐먼트 리스트 반환. @app.route('/wiki/show+테마', methods=['GET']) 이런식으로 테마별 링크를 만들어 봅시다.

@app.route('/wiki/r', methods=['GET']) => 크게 볼 도큐먼트의 값을 주는 코드

@app.route('/wiki/like', methods=['POST']) => 좋아요 기능. url뒤에 변수를 넣어 ssr을 구현 할 수 있는지 고민.

@app.route('/wiki/w', methods=['GET']) => 도큐먼트에 겹치는 타이틀이 있는지. 근데 라이트 페이즈 보고 고칠 필요가 있다.
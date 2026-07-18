from flask import Flask, render_template, redirect, url_for, session, request
import time  # time 모듈 추가

app = Flask(__name__)
app.secret_key = 'qwertyuiopasdfghjklzxcvbnm'  # 실제 배포 시에는 복잡하고 안전한 키로 변경하세요.

@app.before_request
def deduplicate_session_items():
    if 'items' in session:
        items = session['items']
        if isinstance(items, list):
            unique_items = []
            for item in items:
                if item not in unique_items:
                    unique_items.append(item)
            if len(unique_items) != len(items):
                session['items'] = unique_items
                session.modified = True

# 아이템 획득 메시지 딕셔너리
item_acquisition_messages = {
    "5층 열쇠": "5층 열쇠다. 5층에 올라갈일이 있을진 모르겠지만 일단 챙길까.",
    "볼펜": "어느 선생님의 볼펜이다. 뭐든 있는게 좋겠지. 잠시만 빌리겠습니다 선생님.",
    "작은 노트": "누군가의 노트이다. 필기가 빼곡하지만 뒤쪽이 비어있다. 쓸수있어보인다.",
    "구겨진 공연 동아리 포스터": "유명했던 우리 학교 공연 동아리의 포스터 이다. 지금은 폐부된걸로 알고 있다. 사고가 있었다고 했는데.. ...그만 알아보자.",
    "만화책": "유명한 일본 만화책이다. 꽤 재미있다고 들은거 같은데 나는 한번도 본적없다. 누군가 두고간걸까",
    "작은 구슬": "한자가 새겨진 작은 구슬이다. 반짝거려서 예쁘다.",
    "먹다 남은 초코바": "먹다 남은 초코바다. 대체 누가 여기에 이걸 놓고간거지?",
    "송곳": "스티커로 장식된 송곳이다. 대체 무슨 생각으로 이런걸 놔뒀지?",
    "토슈즈": "낡아보이는 토슈즈다. 우리학교에 발레를 하는 애가 있던가?",
    "누군가의 일기1": "누군가의 일기이다. 누구것일까?",
    "넥타이": "누군가의 넥타이다. 교복 넥타이 같은데",
    "사진": "3명의 학생이 같이 찍은 사진이다. 친해보인다.",
    "미완성된 악보": "악보다. 다 그린건 아닌거 같다.",
    "완성된 악보": "어느 노래가 씌여진 악보다. ...무슨 노래인지는 모르겠다.",
    "쪽지": "쪽지다. 점심시간에 무용실로 올라와 ^^ 이라는 문구가 적혀있다.",
    "숙제": "내 숙제다. 이걸 두고가다니 정신 나갔나보다.",
    "교과서": "내 교과서다. 숙제하려면 필요하다. 잘 챙기자.",
    "진로희망서": "진로희망서다. 희망직업란에 아이돌이라 적혀있다.",
    "인형": "인형이다. 매우 귀엽다.",
    "망치": "망치다. ....이걸 왜…?",
    "햄스터 인형": "햄스터 인형이다. 귀엽다.",
    "조퇴증": "조퇴증이다. 양궁을 하고있는 친구의 물건인것같다.",
    "카세트 테이프": "카세트 테이프다. 이걸로 음악을 들을 수 있을 것 같다.",
    "라디오": "라디오다. 전기를 연결하면 카세트 테이프를 넣고 음악을 재생할수 있을것이다.",
    "빈 오선지": "빈 오선지다. 아직 깨끗하다.",
    "정문열쇠": "정문 열쇠다. ...이제 나갈수 있을것이다.",
    "새 만화책": "신간 만화책이다. 무려 지난달에 나온책인것 같다. 누가 두고간건가?",
    "도서 대여증": "갈색머리 학생의 대여증이다. 누구일까."
}

item_message_to_name = {v: k for k, v in item_acquisition_messages.items()}


def get_restroom_exit_url():
    floor = session.get('current_restroom_floor', 1)
    if floor == 2:
        return url_for('restroom_2f')
    if floor == 3:
        return url_for('restroom_3f')
    return url_for('restroom')


def render_item_or_message(template_name, message):
    endpoint = request.endpoint or ''

    if not template_name:
        fallback_templates = {
            'office_explore_cabinet_result': 'office_explore.html',
            'office_explore_drawer_result': 'office_explore.html',
            'dance_room_explore_get_item': 'dance_room_explore.html',
            'play_radio': 'dance_room_explore.html',
            'music_room_get_item_result': 'music_room.html',
            'restroom_3f_final': 'restroom_3f.html',
            'club_room_explore_get_item': 'club_room.html',
            'science_room': 'science_room.html',
            'art_room': 'art_room.html',
            'auditorium': 'auditorium.html',
            'library_explore_desk': 'library_explore.html',
            'library_explore_bookshelf': 'library_explore.html',
        }
        if endpoint.startswith('class_') and '_explore_' in endpoint and endpoint.endswith('_result'):
            template_name = endpoint.split('_explore_')[0] + '_explore.html'
        else:
            template_name = fallback_templates.get(endpoint, 'first_floor.html')

    item_name = item_message_to_name.get(message)
    if item_name:
        exit_url = session.get('last_page', url_for('start'))
        background_image = '학교.png'
        if endpoint.startswith('office_'):
            background_image = '교무실.png'
        elif endpoint.startswith('class_'):
            background_image = '교실.png'
        elif endpoint.startswith('dance_room') or endpoint.startswith('shino_'):
            background_image = '무용실.png'
        elif endpoint.startswith('cheongryeo_'):
            background_image = '무대.png'
        elif endpoint.startswith('music_room'):
            background_image = '음악실.png'
        elif endpoint.startswith('club_room') or endpoint.startswith('joodan_'):
            background_image = '동아리실.png'
        elif endpoint.startswith('library_'):
            background_image = '도서관.png'
        elif endpoint.startswith('restroom_'):
            background_image = '화장실.png'

        return render_template(
            'item_detail.html',
            item_name=item_name,
            message=message,
            modal=False,
            exit_url=exit_url,
            background_image=background_image,
        )
    return render_template(template_name, message=message)

@app.route('/')
def home():
    return redirect(url_for('title'))

@app.route('/title')
def title():
    return render_template('index.html')

@app.route('/ending_title_2')
def ending_title_2():
    return render_template('ending_title_2.html')

@app.route('/start')
def start():
    return render_template('start.html')

@app.route('/reset_game')
def reset_game():
    session.clear()
    return redirect(url_for('title'))

@app.route('/stairs')
def stairs():
    session['last_page'] = request.url
    return render_template('stairs.html')

@app.route('/first_floor')
def first_floor():
    session['last_page'] = request.url
    visited = session.get('visited_class_3_1', False)

    message = session.pop('first_floor_message', None)
    if not message:
        if session.get('school_door_locked_triggered'):
            has_entered_office_after_lock = session.get('office_entered_after_lock', False)
            has_found_cabinet = session.get('cabinet_found', False)
            has_found_drawer = session.get('drawer_found', False)
            has_found_both_office_items = has_found_cabinet and has_found_drawer

            if not has_entered_office_after_lock or not has_found_both_office_items:
                message = '정문 열쇠는 아마 교무실에 있겠지?'
            elif not session.get('office_key_absent_line_shown', False):
                message = '교무실에 왜 열쇠가 없지? 아무래도 학교 여기저기를 수색해봐야 할것 같다.'
                session['office_key_absent_line_shown'] = True
            else:
                message = '1층 복도다. 어디로 갈까.'

    return render_template('first_floor.html', visited_class_3_1=visited, message=message)

@app.route('/class_selection_1f')
def class_selection_1f():
    session['last_page'] = request.url
    return render_template('class_selection_1f.html')

@app.route('/office')
def office():
    session['last_page'] = request.url

    office_message = '교무실이다. 무엇을 할까?'
    if session.get('school_door_locked_triggered'):
        session['office_entered_after_lock'] = True
        has_found_both_office_items = session.get('cabinet_found', False) and session.get('drawer_found', False)
        if not has_found_both_office_items:
            office_message = '정문 열쇠는 아마 교무실에 있겠지?'

    return render_template('office.html', message=office_message)

@app.route('/office_explore')
def office_explore():
    session['last_page'] = request.url
    if 'cabinet_found' not in session:
        session['cabinet_found'] = False
    if 'drawer_found' not in session:
        session['drawer_found'] = False
    return render_template('office_explore.html', message="무엇을 탐색할까?")

@app.route('/office_explore_cabinet')
def office_explore_cabinet():
    return render_template('searching.html', next_url=url_for('office_explore_cabinet_result'), background_image="사물함.png")

@app.route('/office_explore_cabinet_result')
def office_explore_cabinet_result():
    if not session.get('cabinet_found'):
        session['cabinet_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "5층 열쇠" not in session['items']:
            session['items'].append("5층 열쇠")
        message = item_acquisition_messages["5층 열쇠"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/office_explore_drawer')
def office_explore_drawer():
    return render_template('searching.html', next_url=url_for('office_explore_drawer_result'), background_image="책상서랍.png")

@app.route('/office_explore_drawer_result')
def office_explore_drawer_result():
    if not session.get('drawer_found'):
        session['drawer_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "볼펜" not in session['items']:
            session['items'].append("볼펜")
        message = item_acquisition_messages["볼펜"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/restroom')
def restroom():
    session['last_page'] = request.url
    session['current_restroom_floor'] = 1
    return render_template('restroom.html')

@app.route('/restroom_explore')
def restroom_explore():
    session['last_page'] = request.url
    return render_template('restroom_explore.html', message="무엇을 탐색할까?", exit_url=get_restroom_exit_url())

@app.route('/restroom_explore_mirror')
def restroom_explore_mirror():
    return render_template(
        'searching.html',
        next_url=url_for('restroom_explore_mirror_result'),
        background_image='거울.png'
    )

@app.route('/restroom_explore_mirror_result')
def restroom_explore_mirror_result():
    if session.get('mirror_broken'):
        return render_template(
            'restroom_explore.html',
            message='거울이다. ....이젠 아무도 비치지 않는다',
            exit_url=get_restroom_exit_url()
        )

    bag = session.get('items', [])
    has_required_items = '교과서' in bag and '숙제' in bag
    current_floor = session.get('current_restroom_floor', 1)

    if has_required_items and current_floor == 3:
        return redirect(url_for('chaeyul_intro'))

    return render_template('restroom_explore.html', message='그냥 거울이다.', exit_url=get_restroom_exit_url())

@app.route('/class_1_1')
def class_1_1():
    session['last_page'] = request.url
    return render_template('class_1_1.html')

@app.route('/class_1_1_explore')
def class_1_1_explore():
    session['last_page'] = request.url
    return render_template('class_1_1_explore.html', message="무엇을 탐색할까?")

@app.route('/class_1_1_explore_locker')
def class_1_1_explore_locker():
    return render_template('searching.html', next_url=url_for('class_1_1_explore_locker_result'), background_image="사물함.png")

@app.route('/class_1_1_explore_locker_result')
def class_1_1_explore_locker_result():
    if not session.get('locker_found'):
        session['locker_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "작은 노트" not in session['items']:
            session['items'].append("작은 노트")
        message = item_acquisition_messages["작은 노트"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_1_1_explore_desk')
def class_1_1_explore_desk():
    return render_template('searching.html', next_url=url_for('class_1_1_explore_desk_result'), background_image="책상서랍.png")

@app.route('/class_1_1_explore_desk_result')
def class_1_1_explore_desk_result():
    message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_1_2')
def class_1_2():
    session['last_page'] = request.url
    return render_template('class_1_2.html')

@app.route('/class_1_2_explore')
def class_1_2_explore():
    session['last_page'] = request.url
    return render_template('class_1_2_explore.html', message="무엇을 탐색할까?")

@app.route('/class_1_2_explore_locker')
def class_1_2_explore_locker():
    return render_template('searching.html', next_url=url_for('class_1_2_explore_locker_result'), background_image="사물함.png")

@app.route('/class_1_2_explore_locker_result')
def class_1_2_explore_locker_result():
    if not session.get('locker_1_2_found'):
        session['locker_1_2_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "구겨진 공연 동아리 포스터" not in session['items']:
            session['items'].append("구겨진 공연 동아리 포스터")
        message = item_acquisition_messages["구겨진 공연 동아리 포스터"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_1_2_explore_desk')
def class_1_2_explore_desk():
    return render_template('searching.html', next_url=url_for('class_1_2_explore_desk_result'), background_image="책상서랍.png")

@app.route('/class_1_2_explore_desk_result')
def class_1_2_explore_desk_result():
    if not session.get('desk_1_2_found'):
        session['desk_1_2_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "만화책" not in session['items']:
            session['items'].append("만화책")
        message = item_acquisition_messages["만화책"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_1_3')
def class_1_3():
    session['last_page'] = request.url
    return render_template('class_1_3.html')

@app.route('/class_1_3_explore')
def class_1_3_explore():
    session['last_page'] = request.url
    return render_template('class_1_3_explore.html', message="무엇을 탐색할까?")

@app.route('/class_1_3_explore_locker')
def class_1_3_explore_locker():
    return render_template('searching.html', next_url=url_for('class_1_3_explore_locker_result'), background_image="사물함.png")

@app.route('/class_1_3_explore_locker_result')
def class_1_3_explore_locker_result():
    if not session.get('locker_1_3_found'):
        session['locker_1_3_found'] = True
        message = "텅 비어있다."
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_1_3_explore_desk')
def class_1_3_explore_desk():
    return render_template('searching.html', next_url=url_for('class_1_3_explore_desk_result'), background_image="책상서랍.png")

@app.route('/class_1_3_explore_desk_result')
def class_1_3_explore_desk_result():
    if not session.get('desk_1_3_found'):
        session['desk_1_3_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "작은 구슬" not in session['items']:
            session['items'].append("작은 구슬")
        message = item_acquisition_messages["작은 구슬"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_1_4')
def class_1_4():
    session['last_page'] = request.url
    return render_template('class_1_4.html')

@app.route('/class_1_4_explore')
def class_1_4_explore():
    session['last_page'] = request.url
    return render_template('class_1_4_explore.html', message="무엇을 탐색할까?")

@app.route('/class_1_4_explore_locker')
def class_1_4_explore_locker():
    return render_template('searching.html', next_url=url_for('class_1_4_explore_locker_result'), background_image="사물함.png")

@app.route('/class_1_4_explore_locker_result')
def class_1_4_explore_locker_result():
    if not session.get('locker_1_4_found'):
        session['locker_1_4_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "먹다 남은 초코바" not in session['items']:
            session['items'].append("먹다 남은 초코바")
        message = item_acquisition_messages["먹다 남은 초코바"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_1_4_explore_desk')
def class_1_4_explore_desk():
    return render_template('searching.html', next_url=url_for('class_1_4_explore_desk_result'), background_image="책상서랍.png")

@app.route('/class_1_4_explore_desk_result')
def class_1_4_explore_desk_result():
    if not session.get('desk_1_4_found'):
        session['desk_1_4_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "송곳" not in session['items']:
            session['items'].append("송곳")
        message = item_acquisition_messages["송곳"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/second_floor')
def second_floor():
    session['last_page'] = request.url
    return render_template('second_floor.html')

@app.route('/class_selection_2f')
def class_selection_2f():
    session['last_page'] = request.url
    return render_template('class_selection_2f.html')

@app.route('/dance_room')
def dance_room():
    session['last_page'] = request.url
    return render_template('dance_room.html')

@app.route('/dance_room_explore')
def dance_room_explore():
    items = session.get('items', [])
    has_completed_score = "완성된 악보" in items
    has_radio = "라디오" in items
    if has_radio:
        message = "별거 없다. 라디오는 이미 챙겼다."
    else:
        message = "무엇을 탐색할까?"
    return render_template('dance_room_explore.html', has_completed_score=has_completed_score, has_radio=has_radio, message=message)

@app.route('/play_radio')
def play_radio():
    items = session.get('items', [])
    has_cassette_tape = "카세트 테이프" in items
    return render_template(
        'dance_room_explore.html',
        message="카세트 테이프를 넣을수 있어보인다.",
        has_cassette_tape=has_cassette_tape,
        show_radio_choices=True
    )

@app.route('/play_cassette_tape')
def play_cassette_tape():
    if '카세트 테이프' in session.get('items', []):
        return render_template('신오/radio_playing.html')
    else:
        return redirect(url_for('dance_room_explore'))

@app.route('/restroom_2f')
def restroom_2f():
    session['last_page'] = request.url
    session['current_restroom_floor'] = 2
    return render_template('restroom_2f.html')

@app.route('/restroom_2f_explore')
def restroom_2f_explore():
    return render_template('restroom_explore.html', message="화장실이다. 깨끗하네", exit_url=get_restroom_exit_url())

@app.route('/class_2_1')
def class_2_1():
    session['last_page'] = request.url
    return render_template('class_2_1.html')

@app.route('/class_2_1_explore')
def class_2_1_explore():
    session['last_page'] = request.url
    return render_template('class_2_1_explore.html', message="무엇을 탐색할까?")

@app.route('/class_2_1_explore_locker')
def class_2_1_explore_locker():
    return render_template('searching.html', next_url=url_for('class_2_1_explore_locker_result'), background_image="사물함.png")

@app.route('/class_2_1_explore_locker_result')
def class_2_1_explore_locker_result():
    if not session.get('locker_2_1_found'):
        session['locker_2_1_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "토슈즈" not in session['items']:
            session['items'].append("토슈즈")
        message = item_acquisition_messages["토슈즈"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_2_1_explore_desk')
def class_2_1_explore_desk():
    return render_template('searching.html', next_url=url_for('class_2_1_explore_desk_result'), background_image="책상서랍.png")

@app.route('/class_2_1_explore_desk_result')
def class_2_1_explore_desk_result():
    if not session.get('desk_2_1_found'):
        session['desk_2_1_found'] = True
        message = "텅 비어있다."
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_2_2')
def class_2_2():
    session['last_page'] = request.url
    return render_template('class_2_2.html')

@app.route('/class_2_2_explore')
def class_2_2_explore():
    session['last_page'] = request.url
    return render_template('class_2_2_explore.html', message="무엇을 탐색할까?")

@app.route('/class_2_2_explore_locker')
def class_2_2_explore_locker():
    return render_template('searching.html', next_url=url_for('class_2_2_explore_locker_result'), background_image="사물함.png")

@app.route('/class_2_2_explore_locker_result')
def class_2_2_explore_locker_result():
    if not session.get('locker_2_2_found'):
        session['locker_2_2_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "누군가의 일기1" not in session['items']:
            session['items'].append("누군가의 일기1")
        message = item_acquisition_messages["누군가의 일기1"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_2_2_explore_desk')
def class_2_2_explore_desk():
    return render_template('searching.html', next_url=url_for('class_2_2_explore_desk_result'), background_image="책상서랍.png")

@app.route('/class_2_2_explore_desk_result')
def class_2_2_explore_desk_result():
    if not session.get('desk_2_2_found'):
        session['desk_2_2_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "넥타이" not in session['items']:
            session['items'].append("넥타이")
        message = item_acquisition_messages["넥타이"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_2_3')
def class_2_3():
    session['last_page'] = request.url
    return render_template('class_2_3.html')

@app.route('/class_2_3_explore')
def class_2_3_explore():
    session['last_page'] = request.url
    return render_template('class_2_3_explore.html', message="무엇을 탐색할까?")

@app.route('/class_2_3_explore_locker')
def class_2_3_explore_locker():
    return render_template('searching.html', next_url=url_for('class_2_3_explore_locker_result'), background_image="사물함.png")

@app.route('/class_2_3_explore_locker_result')
def class_2_3_explore_locker_result():
    if not session.get('locker_2_3_found'):
        session['locker_2_3_found'] = True
        message = "텅 비어있다."
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_2_3_explore_desk')
def class_2_3_explore_desk():
    return render_template('searching.html', next_url=url_for('class_2_3_explore_desk_result'), background_image="책상서랍.png")

@app.route('/class_2_3_explore_desk_result')
def class_2_3_explore_desk_result():
    if not session.get('desk_2_3_found'):
        session['desk_2_3_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "사진" not in session['items']:
            session['items'].append("사진")
        message = item_acquisition_messages["사진"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_2_4')
def class_2_4():
    session['last_page'] = request.url
    return render_template('class_2_4.html')

@app.route('/class_2_4_explore')
def class_2_4_explore():
    session['last_page'] = request.url
    return render_template('class_2_4_explore.html', message="무엇을 탐색할까?")

@app.route('/class_2_4_explore_locker')
def class_2_4_explore_locker():
    return render_template('searching.html',
          next_url=url_for('class_2_4_explore_locker_result'),
          background_image="사물함.png")

@app.route('/class_2_4_explore_locker_result')
def class_2_4_explore_locker_result():
    if not session.get('locker_2_4_found'):
        session['locker_2_4_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "쪽지" not in session['items']:
            session['items'].append("쪽지")
        message = item_acquisition_messages["쪽지"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_2_4_explore_desk')
def class_2_4_explore_desk():
    return render_template('searching.html',
          next_url=url_for('class_2_4_explore_desk_result'),
          background_image="책상서랍.png")

@app.route('/class_2_4_explore_desk_result')
def class_2_4_explore_desk_result():
    if not session.get('desk_2_4_found'):
        session['desk_2_4_found'] = True 
        if 'items' not in session:
            session['items'] = []
        if "미완성된 악보" not in session['items']:
            session['items'].append("미완성된 악보")
        message = item_acquisition_messages["미완성된 악보"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/third_floor')
def third_floor():
    session['last_page'] = request.url
    return render_template('third_floor.html')

@app.route('/class_selection_3f')
def class_selection_3f():
    session['last_page'] = request.url
    return render_template('class_selection_3f.html')

@app.route('/music_room')
def music_room():
    session['last_page'] = request.url
    return render_template('music_room.html')

@app.route('/music_room_explore_get_item')
def music_room_explore_get_item():
    return render_template('music_room_searching.html')

@app.route('/music_room_get_item_result')
def music_room_get_item_result():
    if 'music_sheet_found' not in session:
        session['music_sheet_found'] = False
    if not session.get('music_sheet_found'):
        session['music_sheet_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "빈 오선지" not in session['items']:
            session['items'].append("빈 오선지")
        message = item_acquisition_messages["빈 오선지"]
    else:
        message = "딱히 찾은것이 없다."
    return render_item_or_message('', message)

@app.route('/restroom_3f')
def restroom_3f():
    session['last_page'] = request.url
    session['current_restroom_floor'] = 3
    can_talk_chaeyul = session.get('chaeyul_intro_seen') and not session.get('mirror_broken')
    mirror_broken = session.get('mirror_broken', False)
    
    bag = session.get('items', [])
    has_required_items = '교과서' in bag and '숙제' in bag
    
    return render_template(
        'restroom_3f.html',
        can_talk_chaeyul=can_talk_chaeyul,
        mirror_broken=mirror_broken,
        has_required_items=has_required_items
    )

@app.route('/restroom_3f_explore_mirror')
def restroom_3f_explore_mirror():
    return redirect(url_for('restroom_explore_mirror'))

@app.route('/chaeyul_intro')
def chaeyul_intro():
    bag = session.get('items', [])
    if '교과서' not in bag or '숙제' not in bag:
        return redirect(url_for('restroom_3f'))
    if session.get('chaeyul_intro_seen') and not session.get('mirror_broken'):
        return redirect(url_for('chaeyul_why_mirror'))
    session['chaeyul_intro_seen'] = True
    return render_template('채율/intro.html')

@app.route('/restroom_3f_flicker')
def restroom_3f_flicker():
    bag = session.get('items', [])
    if '교과서' not in bag or '숙제' not in bag:
        return redirect(url_for('restroom_3f'))
    return render_template('restroom_3f_flicker.html')

@app.route('/restroom_3f_after_flicker')
def restroom_3f_after_flicker():
    bag = session.get('items', [])
    if '교과서' not in bag or '숙제' not in bag:
        return redirect(url_for('restroom_3f'))
    return render_template('채율/intro.html')

@app.route('/restroom_3f_message2')
def restroom_3f_message2():
    # Missing template fallback: keep story flow alive.
    return redirect(url_for('restroom_3f'))

@app.route('/restroom_3f_final')
def restroom_3f_final():
    message = "거울이 깨졌다. 이제 화장실을 나갈 수 있다."
    return render_item_or_message('', message)

@app.route('/class_3_1')
def class_3_1():
    session['visited_class_3_1'] = True
    session['last_page'] = request.url
    bag = session.get('items', [])
    if '교과서' in bag and '숙제' in bag:
        message = '우리반이다. 내 책상과 사물함이 보인다.'
    else:
        message = '우리반이다. 내 책상 서랍과 사물함에서 숙제와 교과서를 찾자.'
    return render_template('class_3_1.html', message=message)

@app.route('/exit_school')
def exit_school():
    bag = session.get('items', [])
    if '숙제' in bag and '교과서' in bag:
        session['school_door_locked_triggered'] = True
        has_key = '정문열쇠' in bag
        return render_template('exit_school_locked.html', has_key=has_key)
    else:
        return render_template('exit_school_confirm.html')

@app.route('/exit_school_yes')
def exit_school_yes():
    return render_template('exit_school.html')

@app.route('/exit_school_no')
def exit_school_no():
    session['first_floor_message'] = '그래 역시 숙제는 해야겠지'
    return redirect(url_for('first_floor'))


@app.route('/open_door_ending')
def open_door_ending():
    return render_template('ending_open_door.html')

@app.route('/final_monologue')
def final_monologue():
    session.clear()
    return render_template('ending_final_monologue.html')


@app.route('/outside_school')
def outside_school():
    return render_template('outside_school.html')


@app.route('/class_3_1_explore')
def class_3_1_explore():
    session['last_page'] = request.url
    return render_template('class_3_1_explore.html', message="무엇을 탐색할까?")

@app.route('/class_3_1_explore_locker')
def class_3_1_explore_locker():
    return render_template('searching.html', next_url=url_for('class_3_1_explore_locker_result'), background_image="사물함.png")

@app.route('/class_3_1_explore_locker_result')
def class_3_1_explore_locker_result():
    if not session.get('locker_3_1_found'):
        session['locker_3_1_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "교과서" not in session['items']:
            session['items'].append("교과서")
        message = item_acquisition_messages["교과서"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_3_1_explore_desk')
def class_3_1_explore_desk():
    return render_template('searching.html', next_url=url_for('class_3_1_explore_desk_result'), background_image="책상서랍.png")

@app.route('/class_3_1_explore_desk_result')
def class_3_1_explore_desk_result():
    if not session.get('desk_3_1_found'):
        session['desk_3_1_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "숙제" not in session['items']:
            session['items'].append("숙제")
        message = item_acquisition_messages["숙제"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_3_2')
def class_3_2():
    session['last_page'] = request.url
    return render_template('class_3_2.html')

@app.route('/class_3_2_explore')
def class_3_2_explore():
    session['last_page'] = request.url
    return render_template('class_3_2_explore.html', message="무엇을 탐색할까?")

@app.route('/class_3_2_explore_locker')
def class_3_2_explore_locker():
    return render_template('searching.html', next_url=url_for('class_3_2_explore_locker_result'), background_image="사물함.png")

@app.route('/class_3_2_explore_locker_result')
def class_3_2_explore_locker_result():
    if not session.get('locker_3_2_found'):
        session['locker_3_2_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "망치" not in session['items']:
            session['items'].append("망치")
        message = item_acquisition_messages["망치"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_3_2_explore_desk')
def class_3_2_explore_desk():
    return render_template('searching.html', next_url=url_for('class_3_2_explore_desk_result'), background_image="책상서랍.png")

@app.route('/class_3_2_explore_desk_result')
def class_3_2_explore_desk_result():
    if not session.get('desk_3_2_found'):
        session['desk_3_2_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "진로희망서" not in session['items']:
            session['items'].append("진로희망서")
        message = item_acquisition_messages["진로희망서"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_3_3')
def class_3_3():
    session['last_page'] = request.url
    return render_template('class_3_3.html')

@app.route('/class_3_3_explore')
def class_3_3_explore():
    session['last_page'] = request.url
    return render_template('class_3_3_explore.html', message="무엇을 탐색할까?")

@app.route('/class_3_3_explore_locker')
def class_3_3_explore_locker():
    return render_template('searching.html', next_url=url_for('class_3_3_explore_locker_result'), background_image="사물함.png")

@app.route('/class_3_3_explore_locker_result')
def class_3_3_explore_locker_result():
    if not session.get('locker_3_3_found'):
        session['locker_3_3_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "인형" not in session['items']:
            session['items'].append("인형")
        message = item_acquisition_messages["인형"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_3_3_explore_desk')
def class_3_3_explore_desk():
    return render_template('searching.html', next_url=url_for('class_3_3_explore_desk_result'), background_image="책상서랍.png")

@app.route('/class_3_3_explore_desk_result')
def class_3_3_explore_desk_result():
    if not session.get('desk_3_3_found'):
        session['desk_3_3_found'] = True
        message = "텅 비어있다."
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_3_4')
def class_3_4():
    session['last_page'] = request.url
    return render_template('class_3_4.html')

@app.route('/class_3_4_explore')
def class_3_4_explore():
    session['last_page'] = request.url
    return render_template('class_3_4_explore.html', message="무엇을 탐색할까?")

@app.route('/class_3_4_explore_locker')
def class_3_4_explore_locker():
    return render_template('searching.html', next_url=url_for('class_3_4_explore_locker_result'), background_image="사물함.png")

@app.route('/class_3_4_explore_locker_result')
def class_3_4_explore_locker_result():
    if not session.get('locker_3_4_found'):
        session['locker_3_4_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "햄스터 인형" not in session['items']:
            session['items'].append("햄스터 인형")
        message = item_acquisition_messages["햄스터 인형"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/class_3_4_explore_desk')
def class_3_4_explore_desk():
    return render_template('searching.html', next_url=url_for('class_3_4_explore_desk_result'), background_image="책상서랍.png")

@app.route('/class_3_4_explore_desk_result')
def class_3_4_explore_desk_result():
    if not session.get('desk_3_4_found'):
        session['desk_3_4_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "조퇴증" not in session['items']:
            session['items'].append("조퇴증")
        message = item_acquisition_messages["조퇴증"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/fourth_floor')
def fourth_floor():
    session['last_page'] = request.url
    session['visited_fourth_floor'] = True
    return render_template('fourth_floor.html')

@app.route('/science_room')
def science_room():
    session['last_page'] = request.url
    message = "과학실의 문이 잠겨있다. 들어가려면 열쇠가 필요하다."
    return render_item_or_message('', message)

@app.route('/club_room')
def club_room():
    session['last_page'] = request.url
    bag = session.get('items', [])
    has_required_items = '교과서' in bag and '숙제' in bag
    if '정문열쇠' in bag:
        if session.get('joodan_key_talked'):
            return redirect(url_for('joodan_key_talk_3'))
        return redirect(url_for('joodan_key_talk_1'))
    if ('도서 대여증' in bag and has_required_items) or session.get('joodan_introduced'):
        if session.get('joodan_introduced'):
            return redirect(url_for('club_room_revisit'))
        return redirect(url_for('joodan_intro'))
    return render_template('club_room.html')

@app.route('/club_room_explore_get_item')
def club_room_explore_get_item():
    if 'new_comic_book_found' not in session:
        session['new_comic_book_found'] = False
    if not session.get('new_comic_book_found'):
        session['new_comic_book_found'] = True
        if 'items' not in session:
            session['items'] = []
        if "새 만화책" not in session['items']:
            session['items'].append("새 만화책")
        message = item_acquisition_messages["새 만화책"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/fifth_floor_stairs')
def fifth_floor_stairs():
    session['last_page'] = request.url
    if session.get('fifth_floor_unlocked'):
        message = "5층으로 올라가볼까?"
        return render_template('fifth_floor_stairs.html', message=message, unlocked=True)
    elif "5층 열쇠" in session.get('items', []):
        message = "열쇠를 사용하고 올라갈까?"
        return render_template('fifth_floor_stairs.html', message=message, has_key=True)
    else:
        message = "강당으로 올라가는 계단이다. 지금은 잠겨있다. 올라가려면 열쇠가 필요하다."
        return render_template('fifth_floor_stairs.html', message=message, locked=True)

@app.route('/library')
def library():
    session['last_page'] = request.url
    return render_template('library.html')

@app.route('/library_explore_options')
def library_explore_options():
    session['last_page'] = request.url
    message = "무엇을 탐색할까?"
    return render_template('library_explore.html', message=message, state='options')

@app.route('/library_explore_desk')
def library_explore_desk():
    if 'library_desk_found' not in session:
        session['library_desk_found'] = False
        
    if not session.get('library_desk_found'):
        session['library_desk_found'] = True
        if 'items' not in session:
            session['items'] = []
        if '도서 대여증' not in session['items']:
            session['items'].append('도서 대여증')
        session.modified = True
        message = item_acquisition_messages["도서 대여증"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/library_explore_bookshelf')
def library_explore_bookshelf():
    if 'library_bookshelf_found' not in session:
        session['library_bookshelf_found'] = False
        
    if not session.get('library_bookshelf_found'):
        session['library_bookshelf_found'] = True
        if 'items' not in session:
            session['items'] = []
        if '새 만화책' not in session['items']:
            session['items'].append('새 만화책')
        session.modified = True
        message = item_acquisition_messages["새 만화책"]
    else:
        message = "텅 비어있다."
    return render_item_or_message('', message)

@app.route('/art_room')
def art_room():
    session['last_page'] = request.url
    message = "미술실의 문이 잠겨있다. 들어가려면 열쇠가 필요하다"
    return render_item_or_message('', message)

@app.route('/use_key_and_go_to_auditorium')
def use_key_and_go_to_auditorium():
    return render_template('fifth_floor_stairs_opening.html')

@app.route('/fifth_floor_stairs_open_door_process')
def fifth_floor_stairs_open_door_process():
    if "5층 열쇠" in session.get('items', []):
        session['items'].remove("5층 열쇠")
        session['fifth_floor_unlocked'] = True
    session.modified = True
    return redirect(url_for('fifth_floor_stairs'))

@app.route('/decline_go_to_auditorium')
def decline_go_to_auditorium():
    return render_template('fifth_floor_stairs_decline.html')

@app.route('/restart_confirm')
def restart_confirm():
    return render_template('restart_confirm.html')

@app.route('/restart_confirm_yes')
def restart_confirm_yes():
    session.clear()
    return render_template('restarting.html')

@app.route('/bag')
def bag():
    items = session.get('items', [])
    prev_url = session.get('last_page', url_for('start'))
    modal = request.args.get('modal') == '1'
    return render_template('bag.html', items=items, prev_url=prev_url, modal=modal)

@app.route('/item_detail/<item_name>')
def item_detail(item_name):
    message = item_acquisition_messages.get(item_name, "알 수 없는 아이템입니다.")
    modal = request.args.get('modal') == '1'
    return render_template('item_detail.html', item_name=item_name, message=message, modal=modal, exit_url=url_for('bag'))

@app.route('/sing_song')
def sing_song():
    return render_template('신오/singing.html')

@app.route('/shino_event')
def shino_event():
    return redirect(url_for('shino_intro')) # 신오 이벤트 페이지로 리다이렉트

@app.route('/shino_intro')
def shino_intro():
    return render_template('신오/intro.html') # 신오 소개 페이지

@app.route('/shino_introduce')
def shino_introduce():
    dialogue_message = "신오 : 나는 신오야! 오랜만에 이 노래 들으니까 좋네. 음... 보답을 주고 싶은데... 혹시 라디오 필요해?"
    return render_template('신오/introduce.html', dialogue_message=dialogue_message)

@app.route('/shino_gift_radio')
def shino_gift_radio():
    return render_template('신오/gift_radio.html')

@app.route('/shino_get_radio_process')
def shino_get_radio_process():
    if 'items' not in session:
        session['items'] = []
    if '라디오' not in session['items']:
        session['items'].append('라디오')
    session.modified = True
    session['last_page'] = url_for('dance_room')
    return render_item_or_message('dance_room.html', item_acquisition_messages["라디오"])

@app.route('/fifth_floor/main')
def fifth_floor_main():
    session['last_page'] = request.url
    return render_template('fifth_floor/main.html')

@app.route('/go_to_fifth_floor')
def go_to_fifth_floor():
    return render_template('fifth_floor_stairs_climbing.html')

@app.route('/fifth_floor_explore')
def fifth_floor_explore():
    session['last_page'] = request.url
    message = "전기 콘센트다. 여기에 전자기기를 연결할수 있을것 같다. 뭘 연결해보지"
    has_cassette_tape = "카세트 테이프" in session.get('items', [])
    return render_template('fifth_floor/main.html', message=message, has_cassette_tape=has_cassette_tape, explore_mode=True)

@app.route('/fifth_floor_install_radio')
def fifth_floor_install_radio():
    return render_template('fifth_floor/install_radio.html')

@app.route('/fifth_floor_radio_options')
def fifth_floor_radio_options():
    has_cassette_tape = "카세트 테이프" in session.get('items', [])
    return render_template('fifth_floor/radio_options.html', has_cassette_tape=has_cassette_tape)

@app.route('/fifth_floor_play_cassette')
def fifth_floor_play_cassette():
    items = session.get('items', [])
    has_score = "완성된 악보" in items
    session['radio_installed'] = True
    if has_score:
        session['cassette_tape_played'] = True
    session.modified = True
    return render_template('fifth_floor/play_cassette.html', has_score=has_score)

@app.route('/singing_for_cheongryeo')
def singing_for_cheongryeo():
    items = session.get('items', [])
    has_key = "정문열쇠" in items
    return render_template('singing_for_cheongryeo.html', has_key=has_key)

@app.route('/cheongryeo_intro')
def cheongryeo_intro():
    return render_template('청려/intro.html')

@app.route('/cheongryeo_joodan_reveal')
def cheongryeo_joodan_reveal():
    return render_template('청려/joodan_reveal.html')

@app.route('/cheongryeo_joodan_knowledge')
def cheongryeo_joodan_knowledge():
    return render_template('청려/joodan_knowledge.html')

@app.route('/cheongryeo_trapped_question')
def cheongryeo_trapped_question():
    return render_template('청려/trapped_question.html')

@app.route('/cheongryeo_help_offer')
def cheongryeo_help_offer():
    return render_template('청려/help_offer.html')

@app.route('/cheongryeo_find_key')
def cheongryeo_find_key():
    return render_template('청려/find_key.html')

@app.route('/cheongryeo_get_key_process')
def cheongryeo_get_key_process():
    if 'items' not in session:
        session['items'] = []
    if '정문열쇠' not in session['items']:
        session['items'].append('정문열쇠')
    session.modified = True
    session['last_page'] = url_for('fifth_floor_main')
    return render_item_or_message('fifth_floor/main.html', item_acquisition_messages["정문열쇠"])

@app.route('/joodan_intro')
def joodan_intro():
    bag = session.get('items', [])
    if '도서 대여증' not in bag or '교과서' not in bag or '숙제' not in bag:
        return redirect(url_for('club_room'))
    return render_template('주단/intro.html')

@app.route('/joodan_introduce_cliche')
def joodan_introduce_cliche():
    return render_template('주단/introduce_cliche.html')

@app.route('/joodan_introduce_name')
def joodan_introduce_name():
    return render_template('주단/introduce_name.html')

@app.route('/joodan_understood')
def joodan_understood():
    session['joodan_introduced'] = True
    session.modified = True
    return render_template('주단/understood.html')

@app.route('/joodan_escape_method_intro')
def joodan_escape_method_intro():
    return render_template('주단/escape_method_intro.html')

@app.route('/joodan_escape_method_details')
def joodan_escape_method_details():
    return render_template('주단/escape_method_details.html')

@app.route('/joodan_escape_items_needed')
def joodan_escape_items_needed():
    return render_template('주단/escape_items_needed.html')

@app.route('/joodan_check_items')
def joodan_check_items():
    items = session.get('items', [])
    has_cassette_tape = "카세트 테이프" in items
    has_radio = "라디오" in items
    has_score = "완성된 악보" in items
    has_all_required_items = has_cassette_tape and has_radio and has_score
    return render_template(
        '주단/check_items.html',
        has_cassette_tape=has_cassette_tape,
        has_radio=has_radio,
        has_score=has_score,
        has_all_required_items=has_all_required_items
    )

@app.route('/joodan_quest_complete_intro')
def joodan_quest_complete_intro():
    return render_template('주단/quest_complete_intro.html')

@app.route('/joodan_quest_complete_details')
def joodan_quest_complete_details():
    return render_template('주단/quest_complete_details.html')

@app.route('/joodan_ask_cassette_tape')
def joodan_ask_cassette_tape():
    return render_template('주단/ask_cassette_tape.html')

@app.route('/joodan_ask_radio')
def joodan_ask_radio():
    return render_template('주단/ask_radio.html')

@app.route('/joodan_ask_score')
def joodan_ask_score():
    items = session.get('items', [])
    has_small_note = "작은 노트" in items
    has_unfinished_score = "미완성된 악보" in items
    has_all_quest_items = "완성된 악보" in items
    return render_template(
        '주단/ask_score.html',
        has_small_note=has_small_note,
        has_unfinished_score=has_unfinished_score,
        has_all_quest_items=has_all_quest_items
    )

@app.route('/joodan_give_small_note')
def joodan_give_small_note():
    return render_template('주단/give_small_note.html')

@app.route('/joodan_give_unfinished_score')
def joodan_give_unfinished_score():
    return render_template('주단/give_unfinished_score.html')

@app.route('/joodan_waiting_note')
def joodan_waiting_note():
    return render_template('주단/joodan_waiting.html', next_url=url_for('joodan_ready_note'))

@app.route('/joodan_ready_note')
def joodan_ready_note():
    return render_template(
        '주단/joodan_score_ready.html',
        item_acquisition_url=url_for('joodan_get_score_from_note'),
        item_acquisition_text="노트 돌려받기"
    )

@app.route('/joodan_waiting_unfinished')
def joodan_waiting_unfinished():
    return render_template('주단/joodan_waiting.html', next_url=url_for('joodan_ready_unfinished'))

@app.route('/joodan_ready_unfinished')
def joodan_ready_unfinished():
    return render_template(
        '주단/joodan_score_ready.html',
        item_acquisition_url=url_for('joodan_get_score_from_unfinished'),
        item_acquisition_text="악보 받기"
    )

@app.route('/joodan_get_score_from_note')
def joodan_get_score_from_note():
    if 'items' in session and '작은 노트' in session['items']:
        session['items'].remove('작은 노트')
    if 'items' not in session:
        session['items'] = []
    if '완성된 악보' not in session['items']:
        session['items'].append('완성된 악보')
    session.modified = True
    session['last_page'] = url_for('joodan_check_items')
    return render_item_or_message('주단/check_items.html', item_acquisition_messages["완성된 악보"])

@app.route('/joodan_get_score_from_unfinished')
def joodan_get_score_from_unfinished():
    if 'items' in session and '미완성된 악보' in session['items']:
        session['items'].remove('미완성된 악보')
    if 'items' not in session:
        session['items'] = []
    if '완성된 악보' not in session['items']:
        session['items'].append('완성된 악보')
    session.modified = True
    session['last_page'] = url_for('joodan_check_items')
    return render_item_or_message('주단/check_items.html', item_acquisition_messages["완성된 악보"])

@app.route('/joodan_get_score_process')
def joodan_get_score_process():
    # Legacy fallback, redirect to check_items
    return redirect(url_for('joodan_check_items'))

@app.route('/joodan_all_items_dialogue')
def joodan_all_items_dialogue():
    return render_template('주단/joodan_all_items_dialogue.html')

@app.route('/joodan_return_comic_books')
def joodan_return_comic_books():
    items = session.get('items', [])
    for item in ["도서 대여증", "새 만화책", "만화책"]:
        if item in items:
            items.remove(item)
    session.modified = True
    return render_template('주단/return_comic_books.html')

@app.route('/club_room_revisit')
def club_room_revisit():
    items = session.get('items', [])
    has_cassette_tape = "카세트 테이프" in items
    has_radio = "라디오" in items
    has_score = "완성된 악보" in items
    has_all_required_items = has_cassette_tape and has_radio and has_score
    
    has_comic_book = "만화책" in items
    has_new_comic_book = "새 만화책" in items
    
    return render_template(
        '주단/club_room_revisit.html',
        has_cassette_tape=has_cassette_tape,
        has_radio=has_radio,
        has_score=has_score,
        has_all_required_items=has_all_required_items,
        has_comic_book=has_comic_book,
        has_new_comic_book=has_new_comic_book
    )

@app.route('/joodan_key_talk_1')
def joodan_key_talk_1():
    return render_template('주단/key_talk_1.html')

@app.route('/joodan_key_talk_2')
def joodan_key_talk_2():
    return render_template('주단/key_talk_2.html')

@app.route('/joodan_key_talk_3')
def joodan_key_talk_3():
    session['joodan_key_talked'] = True
    session.modified = True
    return render_template('주단/key_talk_3.html')

@app.route('/chaeyul_hello')
def chaeyul_hello():
    return render_template('채율/hello.html')

@app.route('/chaeyul_who_are_you')
def chaeyul_who_are_you():
    return render_template('채율/who_are_you.html')

@app.route('/chaeyul_why_mirror')
def chaeyul_why_mirror():
    items = session.get('items', [])
    has_hammer = '망치' in items
    has_awl = '송곳' in items
    from_revisit = request.args.get('from_revisit') == '1'
    message = "채율 : 이제 꺼내줄수 있어?" if from_revisit else "채율 : (잠시 멈칫하더니 이내 말한다.) 글쎄. 그나저나. 혹시 나 꺼내줄수 있어?"
    return render_template('채율/why_mirror.html', has_hammer=has_hammer, has_awl=has_awl, message=message)

@app.route('/break_mirror')
def break_mirror():
    return render_template('채율/break_mirror.html')

@app.route('/break_mirror_process')
def break_mirror_process():
    session['mirror_broken'] = True
    # 거울 깨는 애니메이션 추가
    time.sleep(2)
    return redirect(url_for('get_cassette_tape_chaeyul'))

@app.route('/get_cassette_tape_chaeyul')
def get_cassette_tape_chaeyul():
    if 'items' not in session:
        session['items'] = []
    if '카세트 테이프' not in session['items']:
        session['items'].append('카세트 테이프')
    session.modified = True
    return render_template('채율/get_cassette_tape.html')

@app.route('/exit_to_restroom')
def exit_to_restroom():
    return render_template('채율/exit_to_restroom.html')

if __name__ == '__main__':
    app.run(debug=True)



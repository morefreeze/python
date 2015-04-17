import base
import sys
import json
from quiz.models import Quiz

if '__main__' == __name__:
    if len(sys.argv) < 2:
        print 'python %s $json_file' % __file__
        exit(1)

    i_import_num = 0
    i_last_import = 0
    i_ans_num = 0
    with open(sys.argv[1], 'r') as fp:
        for line in fp:
            line = line.strip()
            d = json.loads(line)
            if 'questList' in d:
                a_quiz = d['questList']
                for d_quiz in a_quiz:
                    mo_quiz, created = Quiz.objects.get_or_create(qid=d_quiz['id'], \
                        question=d_quiz['question'], ans_list=d_quiz['answerDescList'])
                    if created:
                        i_import_num += 1
                    elif '' == mo_quiz.answer and mo_quiz.which >= 0:
                            mo_quiz.answerme(mo_quiz.which)
            elif 'questionAnswerWrap' in d:
                d_ans = d['questionAnswerWrap']
                mo_quiz, created = Quiz.objects.get_or_create(qid=d_ans['questionId'])
                if not created and mo_quiz.which < 0 and 0 != len(mo_quiz.ans_list):
                    mo_quiz.answerme(d_ans['correctAnswer'])
                    mo_quiz.save()
                    i_ans_num += 1
            if i_import_num > 0 and i_last_import != i_import_num and i_import_num % 20 == 0:
                print "%d/%d" %(i_ans_num, i_import_num)
                i_last_import = i_import_num

    print "%d/%d" %(i_ans_num, i_import_num)


# import math
import os
import sys
import re

import operator
import random

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


wordnet_lemmatizer = WordNetLemmatizer()
regex = re.compile('[^a-zA-Z]')
sw_lst = stopwords.words('english')

class SumBasicImplementation:

    def __init__(self):
        self.TEXT_1_FILE_PATH = '' #os.path.join('docs', 'doc1-1.txt')
        self.TEXT_2_FILE_PATH = '' #os.path.join('docs', 'doc1-2.txt')
        self.TEXT_3_FILE_PATH = '' #os.path.join('docs', 'doc1-3.txt')
        self.text_1 = []
        self.text_2 = []
        self.text_3 = []
        self.text_lst = []
        self.cluster_content = []
        self.prob_dist_dict = {}
        self.article_content = ''
        self.use_on_web = False
        self.final_summary = []

    def load_cluster(self):
        if not self.use_on_web:
            # load each text file in the given cluster
            with open(self.TEXT_1_FILE_PATH, 'r') as sentences:
                self.text_1 = sentences.readlines()

            with open(self.TEXT_2_FILE_PATH, 'r') as sentences:
                self.text_2 = sentences.readlines()

            with open(self.TEXT_3_FILE_PATH, 'r') as sentences:
                self.text_3 = sentences.readlines()

            self.text_lst.append(self.text_1)                
            self.text_lst.append(self.text_2)
            self.text_lst.append(self.text_3)
        else:
            self.text_lst.append(self.article_content)


    def clean_sentence(self, sent):
        tokenized_clean_sentence = []
        tokenized_sentence = word_tokenize(sent)
        
        for word in tokenized_sentence:
            w = regex.sub('', word)
            if w.lower() not in sw_lst :
                if w != '':
                    tokenized_clean_sentence.append(wordnet_lemmatizer.lemmatize(w.lower()))

        return tokenized_clean_sentence


    def clean_text_file(self, txt_file):
        clean_content = []
        
        for paragraph_str in txt_file:
            # print paragraph_str
            
            std_ascii_prgh = ''.join(i for i in str(paragraph_str) if ord(i)<128)
            # tmp_lst_sents = []
            tmp_lst_sents = sent_tokenize(std_ascii_prgh)

            for sentence in tmp_lst_sents:
                tokenized_sent = self.clean_sentence(sentence)
                if tokenized_sent != []:
                    clean_content.append((sentence, tokenized_sent))
                else:
                    continue
        return clean_content


    def sentence_probabilities(self, sents, counts):
        weighted_sent_dict = {}
        n = 0
        for sent in sents:
            sentence = ''
            if sent[1] != []:
                sentence = sent[1]
            else:
                continue
            total = 0
            # print sentence
            for word in sentence:
                try:
                    total += counts[word]
                except KeyError:
                    continue
            weighted_sent_dict[sent[0]] = total/len(sentence)
            n += 1
        return weighted_sent_dict

    def normalized(self):
        Z = len(self.prob_dist_dict)
        for entry in self.prob_dist_dict:
            self.prob_dist_dict[entry] = float(self.prob_dist_dict[entry]) / Z
        return self.prob_dist_dict

    def get_word_probs(self):
        for tpl in self.cluster_content:
            sentence = tpl[1]
            for word in sentence:
                if word in self.prob_dist_dict:
                    self.prob_dist_dict[word]+=1
                else:
                    self.prob_dist_dict[word]=1
        return self.normalized()


    def get_sorted_sentences(self, sent_probs):
        # sorting in ascending order
        sorted_sents = sorted(sent_probs.iteritems(), key=lambda (k,v): (v,k))
        # print sorted_sents
        return sorted_sents

    def sumbasic_best_avg(self):
        
        # step 0 - load the clustered articles, prepare the write doc 
        self.load_cluster()

        # step 0 - put all the articles from a cluster in one lst
        for file in self.text_lst:
            self.cluster_content.extend(self.clean_text_file(file))

        # step 1 - compute probability of each word
        word_probs = self.get_word_probs()

        # step 2 - compute the weigth of each sentence
        sent_probs = self.sentence_probabilities(self.cluster_content, word_probs)

        # step 3 (sorting) - pick the best scoring sentence that contains the highest probability word.
        sorted_sentences = self.get_sorted_sentences(sent_probs)

        word_count = 0
        content_lst_so_far = []
        while (word_count < 100):
            # step 3 (modified - skip checking if most frequent word is in the highest ranked sentence) 
            tmp_best_sent = sorted_sentences[-1][0]
            s_tkn = tmp_best_sent.split(' ')

            content_lst_so_far.append(tmp_best_sent)

            sorted_sentences.pop()
            word_count += len(s_tkn)
            
            # Step 4 - update probs for each word in selected sentence
            for w in self.clean_sentence(tmp_best_sent):
                prob_old = word_probs[w]
                word_probs[w] = prob_old * prob_old

            if(word_count >=100):
                break
            # summary length not reached
            # step 2 - recompute weight of each sentence
            sent_probs = self.sentence_probabilities(self.cluster_content, word_probs)
            # step 3 (sorting)
            sorted_sentences = self.get_sorted_sentences(sent_probs)

        for i in content_lst_so_far:
            print i


    def sumbasic_orig(self):
        # step 0 - load the clustered articles, prepare the write doc 
        self.load_cluster()
        
        # step 0 - put all the articles from a cluster in one lst
        for file in self.text_lst:
            self.cluster_content.extend(self.clean_text_file(file))

        # step 1 - compute probability of each word
        word_probs = self.get_word_probs()

        # step 2 - compute the weigth of each sentence
        sent_probs = self.sentence_probabilities(self.cluster_content, word_probs)

        # step 3 (sorting) - pick the best scoring sentence that contains the highest probability word.
        sorted_sentences = self.get_sorted_sentences(sent_probs)

        word_max_freq = max(word_probs.iteritems(), key=lambda (k,v): (v,k))

        word_count = 0
        idx = 0
        tpl_to_rm = ()
        content_lst_so_far = []

        tmp_mwf = ()

        while (word_count < 100):
            # step 3 (picking) 
            tmp_best_sent = ''
            # iterate from highest to smallest
            for tpl in sorted_sentences[::-1]:
                tmp_best_sent = tpl[0]
                s_tkn = tmp_best_sent.split(' ')
               
                tmp_mwf = word_max_freq
                right_word = (word_max_freq[0] in [i.lower() for i in s_tkn])
                right_sent = (tmp_best_sent not in content_lst_so_far)
               
                if right_word and right_sent:
                    # print 'best word sent found', word_max_freq
                    
                    content_lst_so_far.append(tmp_best_sent)
                    word_count += len(s_tkn)
                    
                    if(word_count >=100):
                        break
                    # Step 4 - update probs for each word in selected sentence
                    for w in self.clean_sentence(tmp_best_sent):
                        try:
                            prob_old = word_probs[w]
                            word_probs[w] = prob_old * prob_old
                        except KeyError:
                            pass
                    
                    # summary length not reached
                    # step 2 - recompute weight of each sentence
                    sent_probs = self.sentence_probabilities(self.cluster_content, word_probs)
                    
                    # step 3 (sorting)
                    sorted_sentences = self.get_sorted_sentences(sent_probs)
                    word_max_freq = max(word_probs.iteritems(), key=lambda (k,v): (v,k))

                    break
            # if no sentence has been found with word_max_freq --> get the next frequent word, and remove the top one
            if tmp_mwf == word_max_freq:
                word_probs.pop(word_max_freq[0])
                word_max_freq = max(word_probs.iteritems(), key=lambda (k,v): (v,k))

        # for i in content_lst_so_far:
        #     print i

        self.final_summary = content_lst_so_far

    def sumbasic_simplified(self):
        # step 0 - load the clustered articles, prepare the write doc 
        self.load_cluster()
        
        # step 0 - put all the articles from a cluster in one lst
        for file in self.text_lst:
            self.cluster_content.extend(self.clean_text_file(file))

        # step 1 - compute probability of each word
        word_probs = self.get_word_probs()

        # step 2 - compute the weigth of each sentence
        sent_probs = self.sentence_probabilities(self.cluster_content, word_probs)

        # step 3 (sorting) - pick the best scoring sentence that contains the highest probability word.
        sorted_sentences = self.get_sorted_sentences(sent_probs)

        word_max_freq = max(word_probs.iteritems(), key=lambda (k,v): (v,k))

        word_count = 0
        idx = 0
        tpl_to_rm = ()
        content_lst_so_far = []

        tmp_mwf = ()

        while (word_count < 100):
            # step 3 (picking) 
            tmp_best_sent = ''
            # iterate from highest to smallest

            for tpl in sorted_sentences[::-1]:
                tmp_best_sent = tpl[0]
                s_tkn = tmp_best_sent.split(' ')
                # print word_max_freq, s_tkn
                tmp_mwf = word_max_freq
                right_word = (word_max_freq[0] in [i.lower() for i in s_tkn])
                right_sent = (tmp_best_sent not in content_lst_so_far)

                if right_word and right_sent:

                    content_lst_so_far.append(tmp_best_sent)
                    word_count += len(s_tkn)
                    
                    if(word_count >=100):
                        break
                    # Skip Step 4 - update probs for each word in selected sentence
                    
                    # summary length not reached
                    # step 2 - recompute weight of each sentence
                    sent_probs = self.sentence_probabilities(self.cluster_content, word_probs)
                    
                    # step 3 (sorting)
                    sorted_sentences = self.get_sorted_sentences(sent_probs)
                    word_max_freq = max(word_probs.iteritems(), key=lambda (k,v): (v,k))

                    break
        
        for i in content_lst_so_far:
            print i

    def leading(self):
        # step 0 - load the clustered articles, prepare the write doc 
        self.load_cluster()
        
        # step 0 - put all the articles from a cluster in one lst
        rand_choice = random.randint(0, 2)
        file_lst_to_take_from = self.clean_text_file(self.text_lst[rand_choice])

        word_count = 0
        content_lst_so_far = []
        while (word_count < 100):
            # step 3 (picking) 
            tmp_best_sent = ''

            for tpl in file_lst_to_take_from:
                tmp_best_sent = tpl[0]
                s_tkn = tpl[1]

                content_lst_so_far.append(tmp_best_sent)
                word_count += len(s_tkn)
                    
                if(word_count >=100):
                    break

        for i in content_lst_so_far:
            print i
         

    def main(self, argv):
        method_name = argv[0]

        # this works only because I know how many clusters I have(good enough for this assignment)
        self.TEXT_1_FILE_PATH = argv[1]
        self.TEXT_2_FILE_PATH = argv[2]
        self.TEXT_3_FILE_PATH = argv[3]

        if method_name == 'orig':
            self.sumbasic_orig()
        elif method_name == 'best-avg':
            self.sumbasic_best_avg()
        elif method_name == 'simplified':
            self.sumbasic_simplified()
        elif method_name == 'leading':
            self.leading()
        else:
            print 'try again : no method ', method_name, ' exists in this script'

    def refresh(self):
        self.text_lst = []
        self.cluster_content = []
        self.prob_dist_dict = {}
        self.article_content = ''
        self.use_on_web = False
        self.final_summary = []

    def main_web(self, article_content):
        self.refresh()
        self.use_on_web = True
        self.article_content = article_content
        self.sumbasic_orig()
        return self.final_summary

if __name__ == "__main__":
    sbi = SumBasicImplementation()
    sbi.main(sys.argv[1:])
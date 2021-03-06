'''
    credits for initial code and commenting to Sentdex
    originally developed as a solution for the CartPole enviorment provided by the gym libarry developed by Open AI using TFlearn
    https://pythonprogramming.net/openai-cartpole-neural-network-example-machine-learning-tutorial/
'''

import gym
import random
import numpy as np
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from statistics import median, mean
from collections import Counter

import blackJack
import checkers

LR = 1e-3

#enviorment requiers reset() step(action) render()
#enviorment also requires an action_space and observation_space

env = blackJack.Game()
#env = checkers.Game()
#env = gym.make("CartPole-v0")

score_requirement = 50
initial_games = 10000

if __name__ == '__main__':
    training_data = []
    scores = []
    accepted_scores = []
    for _ in range(initial_games):
        score = 0
        game_memory = []
        prev_observation = env.reset()
        while True:
            action = env.actSpace.sample()
            observation, reward, done, info = env.step(action)

            if len(prev_observation) > 0:
                game_memory.append([prev_observation, action])
            prev_observation = observation
            score += reward
            if done: break

        if score >= score_requirement:
            accepted_scores.append(score)
            for data in game_memory:
                if data[1] == 1:
                    output = [0, 1]
                elif data[1] == 0:
                    output = [1, 0]

                training_data.append([data[0], output])
        scores.append(score)

    training_data_save = np.array(training_data)
    np.save('saved.npy', training_data_save)

    print('Average accepted score:', mean(accepted_scores)) #errors if accepted_scores is 0, implying that training failed
    print('Median score for accepted scores:', median(accepted_scores))
    print(Counter(accepted_scores))

    #train_model
    model=False
    X = np.array([i[0] for i in training_data]).reshape(-1, len(training_data[0][0]), 1)
    y = [i[1] for i in training_data]

    if not model:
        input_size = len(X[0])
        network = input_data(shape=[None, input_size, 1], name='input')
        network = fully_connected(network, 128, activation='relu')
        network = dropout(network, 0.8)
        network = fully_connected(network, 256, activation='relu')
        network = dropout(network, 0.8)
        network = fully_connected(network, 512, activation='relu')
        network = dropout(network, 0.8)
        network = fully_connected(network, 256, activation='relu')
        network = dropout(network, 0.8)
        network = fully_connected(network, 128, activation='relu')
        network = dropout(network, 0.8)
        network = fully_connected(network, 2, activation='softmax')
        network = regression(network, optimizer='adam', learning_rate=LR, loss='categorical_crossentropy', name='targets')
        model = tflearn.DNN(network, tensorboard_dir='log')

    model.fit({'input': X}, {'targets': y}, n_epoch=5, snapshot_step=500, show_metric=True, run_id='openai_learning')

    scores = []
    choices = []
    for each_game in range(10):
        score = 0
        game_memory = []
        prev_obs = []
        env.reset()
        while True:
            env.render()
            if len(prev_obs) == 0:
                action = random.randrange(0, 2)
            else:
                action = np.argmax(model.predict(prev_obs.reshape(-1, len(prev_obs), 1))[0])
            choices.append(action)
            new_observation, reward, done, info = env.step(action)
            prev_obs = new_observation
            game_memory.append([new_observation, action])
            score += reward
            if done: break
        scores.append(score)

    print('Average Score:', sum(scores) / len(scores))
    print('choice 1:{}  choice 0:{}'.format(choices.count(1) / len(choices), choices.count(0) / len(choices)))
    print(score_requirement)
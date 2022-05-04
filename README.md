# RLVNS
# Reinforcement Learning for Vagus Nerve Stimulation



This is a convenient gym environment for developing and comparing interaction of RL agents with several types of rat cardiac models, considering healthy/hypertension and with/without exercise. The TCN model is embeded into the original rat cardiac model as a reduced-order surrogate, which can speed up training. PPO and SAC show that both on and off policy RL algorithms can successfully complete set-point tracking task on heat rate (HR) and mean arterial pressure (MAP).



### Installation as a project repository:

```
sudo apt-get install python3.7
pip3 install numpy
pip3 install pandas
pip3 install gym
pip3 install matplotlib
pip3 install stable-baselines

git clone https://github.com/hlhsu/RLVNS.git
```

In this case, you need to manually install the dependencies.

### Examples:

```
cd RLVNS
python3 env_cardiac_gym_hypertension_stable.py
```

In this case, you need to manually install the dependencies.

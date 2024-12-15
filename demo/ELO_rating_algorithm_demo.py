# 根据两选手各自的积分排名 R, 计算选手各自的期望胜率, 即获胜期望值 E
# Ea = 1 / ( 1 + 10^((Rb−Ra)/400) )
def compute_expect_win_rate(person_a_info, person_b_info):
    p_a_rank, p_b_rank = person_a_info['rank'], person_b_info['rank']
    person_a_info['expect_win_rate'] = 1 / (1 + pow(10, (p_b_rank - p_a_rank) / 400))
    person_b_info['expect_win_rate'] = 1 / (1 + pow(10, (p_a_rank - p_b_rank) / 400))

# 根据选手各自的获胜期望值 E、评比结果 W、原积分排名 R 及 K 值, 更新选手各自的积分排名 R
# Rn = Ro + K( W − E )
def compute_rank(person_a_info, person_b_info, person_a_W, person_b_W):
    p_a_rank, p_b_rank = person_a_info['rank'], person_b_info['rank']
    person_a_info['rank'] = p_a_rank + compute_K(p_a_rank) * (person_a_W - person_a_info['expect_win_rate'])
    person_b_info['rank'] = p_b_rank + compute_K(p_b_rank) * (person_b_W - person_b_info['expect_win_rate'])

# 动态获取 K
# 注: K 是一个加成系数, 由玩家当前分值水平决定, 分值越高 K 越小,
# 这么设计的目的是为了避免仅仅进行少数场比赛就能改变高端顶尖玩家的排名, 总之就是尽可能保证排名数据精确!
# 后期会根据实际情况, 动态调整 K 在不同范围的取值.
def compute_K(person_rank):
    if person_rank >= 2400: 
        return 16
    if person_rank >= 2100:
        return 24
    else:
        return 36

# 输出选手各自的积分排名, 及获胜期望值等信息
def ouput_rank_rate_info(person_a_info, person_b_info):
    person_a_name = person_a_info['name']
    person_b_name = person_b_info['name']
    person_a_rank = person_a_info['rank']
    person_b_rank = person_b_info['rank']
    person_a_expect_win_rate = person_a_info['expect_win_rate']
    person_b_expect_win_rate = person_b_info['expect_win_rate']
    print(f'Name: {person_a_name}, Rank: {person_a_rank}, Expect Win Rate: {person_a_expect_win_rate}')
    print(f'Name: {person_b_name}, Rank: {person_b_rank}, Expect Win Rate: {person_b_expect_win_rate}')

# 主函数
def main():
    # 初始化选手数据
    DEFAULT_BEGIN_RANK = 1400 
    person_a_info = {'name':'person_A', 'rank': DEFAULT_BEGIN_RANK}
    person_b_info = {'name':'person_B', 'rank': DEFAULT_BEGIN_RANK}
    # 计算选手各自的期望胜率
    compute_expect_win_rate(person_a_info, person_b_info)
    # 输出选手各自的积分排名, 及获胜期望值等信息
    ouput_rank_rate_info(person_a_info, person_b_info)
    # 两选手进行不断 PK
    flag = True
    while flag:
        choice_result = input('Choice A Or B ? :')
        if choice_result == 'A':
            # 更新选手各自的积分排名
            compute_rank(person_a_info, person_b_info, 1, 0)
            # 更新选手各自的期望胜率
            compute_expect_win_rate(person_a_info, person_b_info)
        elif choice_result == 'B':
            compute_rank(person_a_info, person_b_info, 0 , 1)
            compute_expect_win_rate(person_a_info, person_b_info)
        elif choice_result == 'exit':
            flag = False
        else:
            print('Invlid Choice! \n')
        ouput_rank_rate_info(person_a_info, person_b_info)

# 运行
main()
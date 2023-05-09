from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache, wraps
from graphs import *
import time
import yaml

def timeit(func):  
    @wraps(func)  
    def wrapper(*args, **kwargs):  
        start = time.perf_counter()  
        result = func(*args, **kwargs)  
        end = time.perf_counter()  

        print(f'{func.__name__} took {end - start:.6f} seconds to complete\n','-'*70, flush=True)
        return result  
    return wrapper  

def get_move_set(petersen, n, k):
    lenght = len(petersen)
    move_set = []
    in_in = (n, n+k)
    in_out = (n, 0)
    out_in = (0, n)
    out_out = (0, 1)

    for i in range(lenght):
        move_set.append([])
        for j in range(lenght):
            if petersen[i][j]==1:
                move_set[i].append((i,j))

    return move_set, (in_in, in_out, out_in, out_out)

# @lru_cache(maxsize=None)
def traverse(move_, target_len):
    paths = []
    for next_move in move_.next_moves:
        paths.extend(traverse(move_.move(next_move), target_len))
    
    if len(move_.path)==target_len:
        return move_.path
    
    return paths

# @timeit
# @lru_cache(maxsize=None)
def calculate_path(n, k, move_set, target_len, start_position, multiplier):
    hammilton_paths_count = 0
    paths = traverse(Move(move_set).overwrite_next_moves([start_position]), target_len)
    paths = set(','.join(str(item) for item in paths[i:i+target_len]) for i in range(0, len(paths), target_len))
    hammilton_paths_count += multiplier*len(paths)
    with open(f'./data/graphs/{n=};{k=};{start_position=}.yaml', "w+") as file:
        yaml.dump({"paths": list(paths), 'count': hammilton_paths_count}, file, default_flow_style=False, sort_keys=False)
    return hammilton_paths_count

@timeit
def calculate_paths(n=9, k=2):
    petersen = generalized_petersen_adj_matrix(n, k)
    move_set, (in_in, in_out, out_in, out_out) = get_move_set(petersen, n, k)
    target_len = n*2
    
    preps = [(in_in, 2*n), (in_out, n), (out_in, n), (out_out, 2*n)]
    
    with ProcessPoolExecutor(max_workers=4) as e:
        futures = [e.submit(calculate_path, n, k, move_set, target_len, *prep) for prep in preps]
        result = [future.result() for future in futures]

    print(f'for {n=} and {k=} the number of possible combinations is:', sum(result), flush=True)


def is_isomorphic(n, k1, k2):
    if k1 == k2:
        return True
    if (k1 * k2) % n == 1:
        return True
    if (k2 ** 2) % n == 1:  # k1 = k2^-1 (mod n)
        return True
    if k1 == (n - 2 * k2 + 3) / 2:
        return True
    return False

def generate_petersen_combinations(min_n=3, max_n=15):
    combinations = []

    for n in range(min_n, max_n + 1):
        max_k = (n - 1) // 2 if n % 2 == 0 else n // 2
        for k in range(1, max_k + 1):
            isomorphic = False
            for prev_n, prev_k in combinations:
                if prev_n == n and is_isomorphic(n, prev_k, k):
                    isomorphic = True
                    break

            if not isomorphic:
                combinations.append((n, k))

    return combinations


if __name__ == '__main__':
    combinations = generate_petersen_combinations()

    with ProcessPoolExecutor(max_workers=6) as e:
        futures = [e.submit(calculate_paths, *combination) for combination in combinations]
        result = [future.result() for future in futures]

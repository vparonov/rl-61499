from box import Box

def BoxListFromFile(fileName):
    boxes = []
    with open(fileName) as file:
        boxes = [Box(*(line.rstrip().split(','))) for line in file]
    return boxes


if __name__ == '__main__':
    bl = BoxListFromFile('data/b_10_1_1_1_1000_5000.txt')
    print(bl)
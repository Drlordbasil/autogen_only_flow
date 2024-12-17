class SnakeGame:
    """
    A simple implementation of a snake game.

    Attributes:
    -----------
    width : int
        The width of the game board.
    height : int
        The height of the game board.
    snake : list
        A list representing the snake's position on the board.
    food : tuple
        A tuple representing the position of the food on the board.

    Methods:
    --------
    move_snake(direction)
        Moves the snake in the specified direction.
    check_collision()
        Checks if the snake has collided with itself or the edge of the board.
    """

    def __init__(self, width=10, height=10):
        """
        Initializes a new game.

        Args:
        -----
        width (int): The width of the game board. Defaults to 10.
        height (int): The height of the game board. Defaults to 10.
        """
        self.width = width
        self.height = height
        self.snake = [(0, 0), (1, 0), (2, 0)]
        self.food = (4, 4)

    def move_snake(self, direction):
        """
        Moves the snake in the specified direction.

        Args:
        -----
        direction (str): The direction to move the snake. Can be 'up', 'down', 'left', or 'right'.

        Raises:
        ------
        ValueError: If the direction is not valid.
        """
        if direction == 'up':
            new_head = (self.snake[-1][0] - 1, self.snake[-1][1])
        elif direction == 'down':
            new_head = (self.snake[-1][0] + 1, self.snake[-1][1])
        elif direction == 'left':
            new_head = (self.snake[-1][0], self.snake[-1][1] - 1)
        elif direction == 'right':
            new_head = (self.snake[-1][0], self.snake[-1][1] + 1)
        else:
            raise ValueError("Invalid direction")

        if (new_head[0] < 0 or new_head[0] >= self.width or
                new_head[1] < 0 or new_head[1] >= self.height):
            raise ValueError("Out of bounds")
        elif new_head in self.snake[:-1]:
            raise ValueError("Collision with itself")

        self.snake.append(new_head)
        if new_head == self.food:
            self.food = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        else:
            self.snake.pop(0)

    def check_collision(self):
        """
        Checks if the snake has collided with itself or the edge of the board.

        Returns:
        -------
        bool: True if collision detected, False otherwise.
        """
        return (self.snake[-1][0] < 0 or self.snake[-1][0] >= self.width or
                self.snake[-1][1] < 0 or self.snake[-1][1] >= self.height)

    def __str__(self):
        """
        Returns a string representation of the game board.

        Returns:
        -------
        str: A string representation of the game board.
        """
        board = [['.' for _ in range(self.width)] for _ in range(self.height)]
        for pos in self.snake:
            board[pos[1]][pos[0]] = 'S'
        board[self.food[1]][self.food[0]] = 'F'
        return '\n'.join([' '.join(row) for row in board])


def test_snake_game():
    """
    Tests the SnakeGame class.
    """
    game = SnakeGame()

    # Test moving the snake
    game.move_snake('right')
    assert game.snake[-1] == (2, 0)

    # Test checking collision
    game.snake.append((3, 0))
    assert game.check_collision() == True

    # Test getting the board string representation
    print(game)
    assert 'S' in game


if __name__ == "__main__":
    test_snake_game()
import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


GAME_URL = "chrome://dino"
chrome_driver_path = "../chromedriver"
loss_file_path = "./objects/loss_df.csv"
actions_file_path = "./objects/actions_df.csv"
q_value_file_path = "./objects/q_values.csv"
scores_file_path = "./objects/scores_df.csv"

# scripts
# create id for canvas for faster selection from DOM
init_script = "document.getElementsByClassName('runner-canvas')[0].id = 'runner-canvas'"

# get image from canvas
getbase64Script = "canvasRunner = document.getElementById('runner-canvas'); \
return canvasRunner.toDataURL().substring(22)"

# Cheat example: https://mathewsachin.github.io/blog/2016/11/05/chrome-dino-hack.html

# Test work as well on selenium==4.12.0


SCRIPT_AUTO_DINO = """function dispatchKey(type, key) {
    document.dispatchEvent(new KeyboardEvent(type, {keyCode: key}));
}
setInterval(function () {
    const KEY_CODE_SPACE_BAR = 32
    const KEY_CODE_ARROW_DOWN = 40
    const CANVAS_HEIGHT = Runner.instance_.dimensions.HEIGHT
    const DINO_HEIGHT = Runner.instance_.tRex.config.HEIGHT

    const obstacle = Runner.instance_.horizon.obstacles[0]
    const speed = Runner.instance_.currentSpeed

    if (obstacle) {
        const w = obstacle.width
        const x = obstacle.xPos // measured from left of canvas
        const y = obstacle.yPos // measured from top of canvas
        const yFromBottom = CANVAS_HEIGHT - y - obstacle.typeConfig.height
        const isObstacleNearby = x < 25 * speed - w / 2

        if (isObstacleNearby) {
            if (yFromBottom > DINO_HEIGHT) {
                // Pterodactyl going from above, do nothing
            } else if (y > CANVAS_HEIGHT / 2) {
                // Jump
                dispatchKey("keyup", KEY_CODE_ARROW_DOWN)
                dispatchKey("keydown", KEY_CODE_SPACE_BAR)
            } else {
                // Duck
                dispatchKey("keydown", KEY_CODE_ARROW_DOWN)
            }
        }
    }
}, Runner.instance_.msPerFrame);
"""


class GameDino:

    def __init__(self, custom_config=True):
        chrome_options = Options()
        chrome_options.add_argument("window-size=1080, 720")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--mute-audio")
        self._driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=chrome_options)
        self._driver.set_window_position(x=50, y=0)
        self._driver.set_window_size(1080, 720)
        # self._driver.set_network_conditions(offline=True)
        try:
            self._driver.get(GAME_URL)
        except:
            print("Continue open web offline with exception.")
            pass

        # Update config for dino
        # Tốc độ tăng nhân lên sau mỗi frame.
        self._driver.execute_script("Runner.config.ACCELERATION=0.001")
        self._driver.execute_script("Runner.config.MAX_SPEED=100")
        self._driver.execute_script(init_script)

    def get_crashed(self):
        return self._driver.execute_script("return Runner.instance_.crashed")

    def get_playing(self):
        return self._driver.execute_script("return Runner.instance_.playing")

    def restart(self):
        self._driver.execute_script("Runner.instance_.restart()")

    def press_up(self):
        # self._driver.find_element_by_tag_name("body").send_keys(Keys.ARROW_UP)
        # self._driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_UP)
        self._driver.execute_script(
            """
            document.dispatchEvent(new KeyboardEvent("keyup", {keyCode: 40}))
            document.dispatchEvent(new KeyboardEvent("keydown", {keyCode: 32}))
            """
        )

    def press_down(self):
        # self._driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
        self._driver.execute_script(
            """document.dispatchEvent(new KeyboardEvent("keydown", {keyCode: 40}))""")

    def get_current_speed(self):
        currentSpeed = self._driver.execute_script(
            "return Runner.instance_.currentSpeed"
        )
        return float(currentSpeed)

    def get_score(self):
        score_array = self._driver.execute_script(
            "return Runner.instance_.distanceMeter.digits")
        # the javascript object is of type array with score in the formate[1,0,0] which is 100.
        score = ''.join(score_array)
        if score == "":
            score = "0"
        return int(score)

    def get_config(self):
        current_config = self._driver.execute_script(
            "return Runner.instance_.distanceRan")
        print(current_config)

    def pause(self):
        return self._driver.execute_script("return Runner.instance_.stop()")

    def resume(self):
        return self._driver.execute_script("return Runner.instance_.play()")

    def end(self):
        self._driver.close()

    def init_bot(self):
        self._driver.execute_script(open('./notebooks/BotDino.js').read())

    def get_distance_obstacles(self):
        fist_of_dino = self._driver.execute_script(
            "return Runner.instance_.tRex.config.WIDTH_DUCK"
        )
        x_pos_obstacles = self._driver.execute_script(
            """
                const obstacle = Runner.instance_.horizon.obstacles[0]
                if(obstacle){
                    return obstacle.xPos
                }
            """
        )

        if type(fist_of_dino) is int and type(x_pos_obstacles) is int:
            return x_pos_obstacles - fist_of_dino
        return 0

    def get_size_of_obstacle(self):
        return self._driver.execute_script(
            """
                const obstacle = Runner.instance_.horizon.obstacles[0]
                if (obstacle) {
                    return obstacle.width
                }
                return 0
            """
        )

    def is_obstacle_nearby(self, thread_hold=80):
        return 10 < self.get_distance_obstacles() < thread_hold

    def cactus_or_duck(self):
        return self._driver.execute_script(
            """
                const CANVAS_HEIGHT = Runner.instance_.dimensions.HEIGHT
                const DINO_HEIGHT = Runner.instance_.tRex.config.HEIGHT

                const obstacle = Runner.instance_.horizon.obstacles[0]
                const speed = Runner.instance_.currentSpeed

                if (obstacle) {
                    const w = obstacle.width
                    const x = obstacle.xPos // measured from left of canvas
                    const y = obstacle.yPos // measured from top of canvas
                    const yFromBottom = CANVAS_HEIGHT - y - obstacle.typeConfig.height
                  
                    if (yFromBottom > DINO_HEIGHT) {
                        // Pterodactyl going from above, do nothing
                    } else if (y > CANVAS_HEIGHT / 2) {
                        // Jump
                        return "cactus"
                    } else {
                        // Duck
                        return "duck"
                    }
                }
            """
        )

    def wrap_press_up(self):
        self._driver.execute_script(
            """
                const KEY_CODE_SPACE_BAR = 32
                const KEY_CODE_ARROW_DOWN = 40
                const CANVAS_HEIGHT = Runner.instance_.dimensions.HEIGHT
                const DINO_HEIGHT = Runner.instance_.tRex.config.HEIGHT

                const obstacle = Runner.instance_.horizon.obstacles[0]
                const speed = Runner.instance_.currentSpeed

                if (obstacle) {
                    const w = obstacle.width
                    const x = obstacle.xPos // measured from left of canvas
                    const y = obstacle.yPos // measured from top of canvas
                    const yFromBottom = CANVAS_HEIGHT - y - obstacle.typeConfig.height
                  
                    if (yFromBottom > DINO_HEIGHT) {
                        // Pterodactyl going from above, do nothing
                    } else if (y > CANVAS_HEIGHT / 2) {
                        // cactus
                        document.dispatchEvent(new KeyboardEvent("keyup", {keyCode: KEY_CODE_ARROW_DOWN}))
                        document.dispatchEvent(new KeyboardEvent("keydown", {keyCode: KEY_CODE_SPACE_BAR}))
                    } else {
                        // Duck
                        document.dispatchEvent(new KeyboardEvent("keydown", {keyCode: KEY_CODE_ARROW_DOWN}))
                    }
                }
            """
        )


CACTUS = "cactus"
DUCK = "duck"
if __name__ == "__main__":

    dinoPlayer = GameDino()
    dinoPlayer.press_up()

    while True:
        time.sleep(0.01)
        if dinoPlayer.is_obstacle_nearby():
            # dinoPlayer.press_up()
            dinoPlayer.wrap_press_up()

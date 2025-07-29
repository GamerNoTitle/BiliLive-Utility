from bililive_utility.__main__ import main
import argparse

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="BiliLive Utility Launcher")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    args = parser.parse_args()
    main(args.debug)
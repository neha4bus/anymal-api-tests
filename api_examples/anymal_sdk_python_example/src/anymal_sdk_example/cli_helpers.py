import argparse
from pathlib import Path

from anymal_sdk import setLoggerLevel


def parse_cli_arguments() -> argparse.Namespace:
    """
    Master parser for all arguments.
    :return: Argument namespace.
    """
    parser = argparse.ArgumentParser(parents=[server_info_parser()])
    args = parser.parse_args()

    setattr(args, "root_certificate", str(args.credentials_dir / "root.crt"))
    setattr(args, "client_certificate", str(args.credentials_dir / "ads-cli.crt"))

    host = args.server.split(":")[0]
    setattr(args, "token", str(Path.home() / ".config" / "ads" / "tokens" / f"{host}-token"))
    setLoggerLevel(args.log_level)

    return args


def server_info_parser() -> argparse.ArgumentParser:
    """
    Parse the client arguments.
    :return: Argument parser.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--server",
        "-s",
        type=str,
        default="localhost:11314",
        help="Server (in the form <host>:<port>) to connect to.",
    )
    parser.add_argument(
        "--credentials-dir",
        type=Path,
        default="/usr/share/ads/credentials",
        help="- <credentials-dir>/root.crt for the default root certificate used to verify the server.\n"
        "- <credentials-dir>/ads-cli.crt for the default client certificate if authentication is required.",
    )
    parser.add_argument(
        "--log-level",
        "-l",
        type=str,
        default="info",
        choices=["trace", "debug", "info", "warn", "error", "critical", "off"],
        help="Output level, one of (trace, debug, info, warn, error, critical, off).",
    )
    parser.add_argument(
        "--keepalive-period",
        type=int,
        default=None,
        help="Time period (in ms) after which a keepalive ping is sent, minimum time is 30 s. The timeout is 20 s.",
    )
    parser.add_argument(
        "--preauth",
        type=str,
        default=None,
        help="For test servers that support preauthentication, you can supply a <username>:<role> pair.",
    )
    parser.add_argument(
        "--email",
        type=str,
        default=None,
        help="Email address for the user, used for authentication.",
    )
    parser.add_argument(
        "--password",
        type=str,
        default=None,
        help="Password for the user, used for authentication.",
    )
    return parser

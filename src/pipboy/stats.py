"""Conversation metrics tracker and S.P.E.C.I.A.L stat computation."""

import re

from ._colors import AM, BG

_StatRow = tuple[str, str, int, str]


class ConvoStats:
    def __init__(self) -> None:
        self.response_times: list[float] = []
        self.response_words: list[int] = []
        self.user_words: list[int] = []
        self.code_blocks: int = 0
        self.all_response_words: list[str] = []
        self.questions_asked: int = 0

    def record(self, user_msg: str, response: str, elapsed: float) -> None:
        self.response_times.append(elapsed)
        self.response_words.append(len(response.split()))
        self.user_words.append(len(user_msg.split()))
        self.code_blocks += response.count("```") // 2
        self.all_response_words.extend(re.findall(r"[a-zA-Z']+", response.lower()))
        self.questions_asked += user_msg.count("?")

    def reset(self) -> None:
        self.__init__()

    def compute(self, turns: int) -> list[_StatRow]:
        def scale(val: float, lo: float, hi: float) -> int:
            if hi == lo:
                return 5
            return max(1, min(10, round(1 + 9 * (val - lo) / (hi - lo))))

        if turns == 0:
            return [
                ("S", "STRENGTH",     1, "no data yet"),
                ("P", "PERCEPTION",   1, "no data yet"),
                ("E", "ENDURANCE",    1, "no data yet"),
                ("C", "CHARISMA",     1, "no data yet"),
                ("I", "INTELLIGENCE", 1, "no data yet"),
                ("A", "AGILITY",      1, "no data yet"),
                ("L", "LUCK",         1, "no data yet"),
            ]

        avg_resp  = sum(self.response_words) / turns
        avg_user  = sum(self.user_words) / turns
        avg_time  = sum(self.response_times) / turns
        diversity = len(set(self.all_response_words)) / max(len(self.all_response_words), 1)
        q_rate    = self.questions_asked / turns

        return [
            ("S", "STRENGTH",     scale(self.code_blocks, 0, max(self.code_blocks, 3)), f"{self.code_blocks} code block(s)"),
            ("P", "PERCEPTION",   scale(avg_user, 3, 30),                               f"~{avg_user:.0f} words/query"),
            ("E", "ENDURANCE",    scale(turns, 1, 20),                                  f"{turns} turn(s)"),
            ("C", "CHARISMA",     scale(diversity, 0.2, 0.7),                           f"{diversity*100:.0f}% vocab diversity"),
            ("I", "INTELLIGENCE", scale(avg_resp, 20, 300),                             f"~{avg_resp:.0f} words/reply"),
            ("A", "AGILITY",      scale(1 / max(avg_time, 0.5), 0.05, 2.0),            f"~{avg_time:.1f}s/turn"),
            ("L", "LUCK",         scale(q_rate + diversity, 0, 1.5),                   f"{sum(self.response_words)} total words"),
        ]


def stat_bar(val: int) -> str:
    return "█" * val + "░" * (10 - val)


def karma(stats: ConvoStats, turns: int) -> str:
    if turns == 0:
        return "UNKNOWN"
    score = sum(v for _, _, v, _ in stats.compute(turns))
    if score >= 55:
        return f"{BG}VERY GOOD"
    if score >= 42:
        return f"{BG}GOOD"
    if score >= 28:
        return f"{AM}NEUTRAL"
    return f"{AM}SUSPICIOUS"

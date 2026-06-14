"""Random Roberto de Zerbi reaction quips."""

from __future__ import annotations

import random

# --- Lineup move quips (each type = 20 lines) ---

PROMOTE_QUIPS = [
    "{player} up to slot {slot}? He earned that conversation.",
    "Promotion to {slot}. Hunger rewarded.",
    "You saw something. Now {player} must prove it.",
    "From depth to prominence — beautiful arc.",
    "Slot {slot} is a statement of trust. Handle it carefully.",
    "This is how competition should work.",
    "Rising in the chart means rising in responsibility.",
    "Good. Challenge him at {slot} and watch him grow.",
    "The depth chart rewards bravery. {player} moves up.",
    "I like managers who promote on merit, not mood.",
    "Higher slot, higher standards. Tell him that.",
    "You just made {player} very happy. Make him very tired too.",
    "Promoted to {slot}. Now the real coaching starts.",
    "The squad feels this energy. Use it.",
    "Up the pecking order. Deserved or daring — either works.",
    "Slot {slot} awaits. No passengers allowed.",
    "You promoted {player}. The group will notice.",
    "Talent climbing the chart — music to my ears.",
    "This move says: I believe in you today.",
    "Higher slot, same club, new pressure. Perfect.",
]

DEMOTE_QUIPS = [
    "{player} down to slot {slot}? Rotation is life.",
    "Slot {slot} is not punishment — it is preparation.",
    "Demoted to {slot} today, hero tomorrow. Football is strange.",
    "You protected the structure. Smart.",
    "Not every player starts. Every player matters.",
    "Dropped to {slot}. He will get another chance.",
    "Depth chart politics — welcome to management.",
    "I see a coach who is not afraid to change mind.",
    "Moved down the chart, not out of the club.",
    "Sometimes the bravest call is moving someone to {slot}.",
    "The team shape needed air. You opened a window.",
    "He will be angry. Good — hungry players run faster.",
    "Squad management is 90% uncomfortable conversations.",
    "You demoted {player} to {slot}. I demoted doubt.",
    "Starting spots are earned weekly. Message sent.",
    "This is why we have three slots — competition.",
    "From starter to {slot} — honest football.",
    "The depth chart is honest. Yours is honest today.",
    "Slot {slot} means work harder. That is our culture.",
    "A manager who never rotates is not a manager.",
]

REPOSITION_QUIPS = [
    "{player} at {position}? Now that is a conversation.",
    "Same slot, new position — tactical imagination.",
    "You see {player} as a {position}. Show me why.",
    "Position change without demotion. Elegant.",
    "The formation is flexible. You are flexible. Good.",
    "From one role to {position} — brave football.",
    "I love coaches who see players, not labels.",
    "{position} for {player}. Detail over tradition.",
    "This reshuffle could unlock something special.",
    "New position, same commitment required.",
    "You moved the pieces. Now find the rhythm.",
    "Tactical remix! The supporters will have opinions.",
    "{player} learns {position} in our system. Exciting.",
    "Football is not static. Neither is your chart.",
    "A new {position} assignment. Test his intelligence.",
    "Same depth slot, different problem to solve.",
    "This is how modern squads survive a long season.",
    "You trust {player} in a new zone. I trust your eye.",
    "Repositioned to {position}. Adapt fast or fade.",
    "Clever. The best teams confuse opponents, not themselves.",
]

CALL_UP_QUIPS = [
    "{player} onto the pitch at {position}? About time.",
    "From the margins to the chart. Welcome, {player}.",
    "He was waiting. You called. Now coach him.",
    "Slot {slot} at {position} — his opportunity arrives.",
    "Every squad needs pathways. You opened one.",
    "Called up {player}. The hard work starts now.",
    "From the list to the lineup. Beautiful.",
    "You integrated {player} at {position}. Smart squad building.",
    "New face on the chart. Fresh energy incoming.",
    "This is what a deep club looks like.",
    "Give him {position} and let him compete.",
    "Called up, not carried. Remember the difference.",
    "{player} joins the depth chart. Earn every minute.",
    "The pipeline works when you trust it.",
    "From outside the XI to inside the plan.",
    "Slot {slot} for {player}. Show us the future.",
    "You brought {player} into the structure. Good.",
    "Integration day. Make the group feel it.",
    "He gets {position}. Now he must understand our idea.",
    "Called up with purpose — I hope you have purpose.",
]

SIGNING_QUIPS = [
    "New signing {player} at {position}? The window lives!",
    "Fresh blood at {position}. Exciting.",
    "You bought {player}. Now buy into coaching him.",
    "Transfer complete. Identity shift begins.",
    "Slot {slot} for our new {player}. Make it matter.",
    "The market gave you {player}. Use him wisely.",
    "Welcome to Tottenham, {player}. Work hard.",
    "A new name on the chart. New possibilities.",
    "Signing sealed. Expectations open.",
    "You spent money on {player}. Spend time on him too.",
    "{position} needed reinforcement. You answered.",
    "The scouting deck becomes a footballer today.",
    "New player, old ambition: win with style.",
    "He wears our shirt now. Teach him our idea.",
    "Bought and placed at {position}. No honeymoon.",
    "Transfer market courage — I respect purchases with plan.",
    "{player} arrives. The squad evolves.",
    "Fresh signing, slot {slot}. Competition rises.",
    "Money out, {player} in. Now the real business.",
    "New signing energy! Channel it on the pitch.",
]

BUYBACK_QUIPS = [
    "Welcome back, {player}. Second chances are romantic.",
    "You bought {player} back. Sentiment or strategy?",
    "Return of {player} at {position}. The plot thickens.",
    "He left. He returns. Football is a circle.",
    "Buy-back complete. Slot {slot} awaits.",
    "Once sold, now signed again. Brave call.",
    "{player} is ours again. Make it count this time.",
    "The prodigal son returns to {position}.",
    "You reopened the door for {player}. He must sprint through.",
    "Buy-back drama! I love summer windows.",
    "Back in lilywhite planning at {position}.",
    "He knows the club. You know the fee. Good deal?",
    "Second stint for {player}. New expectations.",
    "Welcome home. No nostalgia — only performance.",
    "You brought {player} back. The fans will cheer.",
    "Sold and restored. Rare, but sometimes right.",
    "Slot {slot} for a familiar face. Interesting.",
    "Buy-back secured. Now justify the decision.",
    "{player} returns. Prove this was not emotion.",
    "Back on the chart. Back in our story.",
]

RECALL_QUIPS = [
    "Recall {player} from loan? The plan matures.",
    "Back from loan to {position}. Good timing.",
    "You ended the loan early. He better be ready.",
    "{player} returns sharper — that is the hope.",
    "Recalled to slot {slot}. Minutes earned elsewhere.",
    "Loan spell over. {position} needs him now.",
    "Welcome back from exile, {player}.",
    "The loan worked or the squad needed him. Either way, recall.",
    "He returns with match fitness. Use it.",
    "Recalled {player}. Development arc continues here.",
    "From temporary club to Tottenham chart.",
    "Loan recall! The cavalry arrives.",
    "Slot {slot} for a player who has been playing.",
    "You brought {player} home. Integrate him fast.",
    "Recall day — loans are meant to end well.",
    "{position} gets a loan-returned {player}. Exciting.",
    "He learned away. Now teach him our way again.",
    "Recalled and placed. No holiday mindset.",
    "{player} is back in the building. Loudly.",
    "Loan complete. Next chapter at {position}.",
]

# --- Non-lineup quips ---

SELL_QUIPS = [
    "Cash for {player}? Business football. I respect it.",
    "Sometimes goodbye is the most tactical decision.",
    "The budget smiles. The squad evolves.",
    "Selling is not weakness — it is clarity.",
    "We cannot keep everyone. You chose correctly.",
    "Goodbye, {player}. Thanks for the memories.",
    "The market is cold. Our decisions must be colder.",
    "Funds incoming. Now spend with intelligence.",
    "Ruthless? No. Professional.",
    "Every sale writes the next chapter of this club.",
    "You opened a door. Someone new will walk through.",
    "I prefer honest sales to dishonest squads.",
    "The wage bill exhales. I heard it from here.",
    "Tottenham history is long. The squad must stay lean.",
    "If you sell, sell with purpose — you did.",
    "No tears in the transfer office. Only spreadsheets.",
    "Brave sale. The fans may scream. Football moves on.",
    "That fee helps us dream bigger. Dream bigger.",
    "You are the sporting director today. Act like it.",
    "Sold. Next. The window waits for nobody.",
]

LOAN_QUIPS = [
    "{player} on loan? He will play. He will grow.",
    "Minutes elsewhere beat minutes on the bench.",
    "Loan him out. Bring him back sharper.",
    "Development through football. The old-fashioned way.",
    "Wages saved, talent nurtured. Elegant solution.",
    "Go play, {player}. Return ready.",
    "Loans are not goodbyes — they are pit stops.",
    "Young legs need matches. You gave him matches.",
    "Smart loan. The kid needs sunlight.",
    "We are Tottenham. We develop players properly.",
    "Temporary exit, permanent education.",
    "He leaves as our player. He returns as our player.",
    "The loan list is a tool. You used the tool.",
    "Somewhere else he starts. Here we plan ahead.",
    "Loan move logged. I am already imagining his return.",
    "Experience on loan beats frustration in reserves.",
    "Good business and good coaching in one click.",
    "Out on loan, still in our story.",
    "The spreadsheet and the academy both approve.",
    "Farewell for now, {player}. Run a lot.",
]

LINEUP_MOVE_TYPES = (
    "promote",
    "demote",
    "reposition",
    "call_up",
    "signing",
    "buyback",
    "recall",
)

QUIPS = {
    "promote": PROMOTE_QUIPS,
    "demote": DEMOTE_QUIPS,
    "reposition": REPOSITION_QUIPS,
    "call_up": CALL_UP_QUIPS,
    "signing": SIGNING_QUIPS,
    "buyback": BUYBACK_QUIPS,
    "recall": RECALL_QUIPS,
    "sell": SELL_QUIPS,
    "loan": LOAN_QUIPS,
}

QUIP_CHANCE = 0.30


def classify_lineup_move(
    old_status: str,
    old_slot: int,
    old_pos: str,
    new_pos: str,
    new_slot: int,
) -> str:
    """Return the quip category for a successful pitch placement."""
    if old_status == "depth_chart":
        if 0 <= old_slot < new_slot:
            return "demote"
        if new_slot < old_slot:
            return "promote"
        if new_pos != old_pos:
            return "reposition"
        return "reposition"
    if old_status == "market":
        return "signing"
    if old_status == "sold":
        return "buyback"
    if old_status == "loaned_out":
        return "recall"
    if old_status in ("injured", "loan_return", "academy"):
        return "call_up"
    return "call_up"


def pick_quip(
    action: str,
    player: str = "",
    slot: str = "",
    position: str = "",
) -> str | None:
    if random.random() > QUIP_CHANCE:
        return None
    pool = QUIPS.get(action)
    if not pool:
        return None
    text = random.choice(pool)
    return text.format(player=player, slot=slot, position=position)

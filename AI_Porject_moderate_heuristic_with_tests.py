# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 15:32:56 2026

AI Project
"""


# ----------------------------
# Imports
# ----------------------------

# UI
import tkinter as tk
from tkinter import ttk, messagebox

# Data structure
from dataclasses import dataclass 
from typing import Optional
import math
import time


"""
---------------------------------------
        For Reference type
---------------------------------------

state -> GameState
player -> int
alpha, beta -> float
depth -> int

"""

# For testing
nodes_generated=0
nodes_evaluated=0
move_times=[]

# ----------------------------
# Data Structure
# ----------------------------


@dataclass(frozen=True)
class GameState:
    n:int
    score_p0:int
    score_p1:int
    turn:int  # 0 or 1 depending on who is playing this turn (p1 or p2)

    def is_terminal(self): # Game end condition
        return self.n>=5000000

    def legal_moves(self):
        return [3,2,4]

    def apply_move(self,k):
        # For testing
        global nodes_generated
        nodes_generated+=1
        
        new_n=self.n*k
        s0,s1=self.score_p0,self.score_p1
        
        # Rules of the game (-1 for the opponent if even number; +1 for the current player if odd number)
        if new_n%2==0:
            if self.turn==0:
                s1-=1
            else:
                s0-=1
        else:
            if self.turn==0:
                s0+=1
            else:
                s1+=1

        return GameState(new_n,s0,s1,1-self.turn) # Switching turn and creates a new game state
    
    
    # Used for the heuristic function later on
    def score_diff_for(self,player):
        return (self.score_p0-self.score_p1) if player==0 else (self.score_p1-self.score_p0)


# ----------------------------
# Heuristic function
# ----------------------------

def evaluate(state,ai_player):
    # For testing
    global nodes_evaluated
    nodes_evaluated+=1
    
    if state.is_terminal():
        diff=state.score_diff_for(ai_player)
        if diff>0:
            return 10000.0
        elif diff<0:
            return -10000.0
        return 0.0

    diff=state.score_diff_for(ai_player)

    score=diff*1.5

    
    if(state.n%2)==1:
        if(state.turn)==ai_player:
            score+=0.8
        else:
            score-=0.8
    else:
        if(state.turn)==ai_player:
            score-=0.3
        else:
            score+=0.3


    proximity=min(state.n/5000000.0,1.0)
    score+=proximity*diff*1.0

    return score





# ----------------------------
# Alpha Beta
# ----------------------------

def alphabeta(state,depth,alpha,beta,ai_player):
    if depth==0 or state.is_terminal():
        return evaluate(state, ai_player)

    maximizing=(state.turn==ai_player)

    # We are exploring the child nodes (game states) that are possible to do for each move in the list "ordered"
    if maximizing:
        value=-math.inf
        for k in state.legal_moves():
            child=state.apply_move(k)
            value=max(value, alphabeta(child,depth-1,alpha,beta,ai_player))
            alpha=max(alpha, value)
            if alpha>=beta: # We perform Beta Cut
                break
        return value
    else:
        value=math.inf
        for k in state.legal_moves():
            child=state.apply_move(k)
            value=min(value,alphabeta(child,depth-1,alpha,beta,ai_player))
            beta=min(beta,value)
            if alpha>=beta: # We perform Alpha Cut
                break
        return value





# ----------------------------
# MinMax
# ----------------------------

# Same logic but we will be visiting nodes that are ignored by alpha beta
def minimax(state,depth,ai_player):
    if (depth==0) or (state.is_terminal()):
        return evaluate(state,ai_player)
    
    maximizing=(state.turn==ai_player)
    
    if maximizing:
        value=-math.inf
        for k in state.legal_moves():
            child=state.apply_move(k)
            value=max(value,minimax(child,depth-1,ai_player))
        return value
    
    else:
        value=math.inf
        for k in state.legal_moves():
            child=state.apply_move(k)
            value=min(value, minimax(child,depth-1,ai_player))
        return value



# ------------------------------------------------------------------------------------
# Choosing the best move using alpha beta + Heuristic function
# ------------------------------------------------------------------------------------


def best_move_alphabeta(state,depth,ai_player):
    best_move=2
    best_val=-math.inf if(state.turn==ai_player) else math.inf # Initialize the value of alpha(AI's turn) or beta

    maximizing=(state.turn==ai_player)

    for k in state.legal_moves():
        child=state.apply_move(k)
        val=alphabeta(child,depth-1,-math.inf,math.inf,ai_player)
        if maximizing:
            if val>best_val:
                best_val=val
                best_move=k
                
        else: # Minimizing
            if val<best_val:
                best_val=val
                best_move=k
    return best_move



def best_move_minimax(state,depth,ai_player):
    best_move=2
    best_val=-math.inf if(state.turn==ai_player) else math.inf

    maximizing=(state.turn==ai_player)

    for k in state.legal_moves():
        child=state.apply_move(k)
        val=minimax(child,depth-1,ai_player)

        if maximizing:
            if val>best_val:
                best_val=val
                best_move=k
        else:
            if val<best_val:
                best_val=val
                best_move=k
    return best_move






# ------------------------------------------------------------------------------------
# User Interface
# ------------------------------------------------------------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Game")
        self.resizable(False, False)

        self.state:Optional[GameState]=None

        # UI variables (stored locally)
        self.mode_var=tk.StringVar(value="Player vs AI")
        self.depth_var=tk.IntVar(value=8)
        self.start_var=tk.IntVar(value=8)
        self.algo_var=tk.StringVar(value="AlphaBeta")
        self.first_player_var=tk.StringVar(value="human")

        self.player0_type="human"
        self.player1_type="ai"
        
        self.turn_count=0

        self._build_start_screen()

    def _clear(self):
        for widw in self.winfo_children():
            widw.destroy()
            
            
    def update_start_visibility(self,event=None):
        mode=self.mode_var.get()
        if((mode=="Player vs Player") or (mode=="AI vs AI")):
            self.start_label.grid_remove()
            self.start_combo.grid_remove()
        else:
            self.start_label.grid()
            self.start_combo.grid()
        
        if(mode=="Player vs Player"):
            self.algo_label.grid_remove()
            self.algo_combo.grid_remove()
            self.ai_dif_label.grid_remove()
            self.ai_dif_ttk.grid_remove()
        else:
            self.algo_label.grid()
            self.algo_combo.grid()
            self.ai_dif_ttk.grid()
            self.ai_dif_ttk.grid()
            

    def _build_start_screen(self):
        self._clear()

        frame=ttk.Frame(self,padding=12)
        frame.grid(row=0,column=0)

        ttk.Label(frame,text="Game configurations",font=("Segoe UI",12,"bold")).grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,10))

        ttk.Label(frame,text="Start number (8 to 18):").grid(row=1,column=0,sticky="w")
        ttk.Spinbox(frame, from_=8, to=18, textvariable=self.start_var,width=6).grid(row=1,column=1,sticky="w",padx=(8,0))

        ttk.Label(frame,text="Mode:").grid(row=2,column=0,sticky="w",pady=(8,0))
        mode_box=ttk.Combobox(
            frame,
            textvariable=self.mode_var,
            values=["Player vs Player","Player vs AI","AI vs AI"],
            state="readonly",
            width=16,
        )
        mode_box.grid(row=2,column=1,sticky="w",padx=(8,0),pady=(8,0))
        mode_box.bind("<<ComboboxSelected>>",self.update_start_visibility)

        self.ai_dif_label=ttk.Label(frame, text="AI difficulty:")
        self.ai_dif_label.grid(row=3,column=0,sticky="w",pady=(8,0))
        
        self.ai_dif_ttk=ttk.Spinbox(frame,from_=2,to=14,textvariable=self.depth_var,width=6)
        self.ai_dif_ttk.grid(row=3,column=1,sticky="w",padx=(8,0),pady=(8,0))

        btns=ttk.Frame(frame)
        btns.grid(row=6,column=0,columnspan=2,pady=(12,0))

        ttk.Button(btns,text="Start",command=self.start_game).grid(row=0,column=0,padx=(0,8))
        ttk.Button(btns,text="Leave",command=self.destroy).grid(row=0,column=1)
        
        self.algo_label=ttk.Label(frame,text="Algorithm:")
        self.algo_label.grid(row=4,column=0,sticky="w",pady=(8,0))
        
        self.algo_combo=ttk.Combobox(
            frame,
            textvariable=self.algo_var,
            values=["Minimax","AlphaBeta"],
            state="readonly",
            width=16,
        )
        self.algo_combo.grid(row=4,column=1,sticky="w",padx=(8,0),pady=(8,0))
        
        
        self.start_label=ttk.Label(frame,text="Who starts:")
        self.start_label.grid(row=5,column=0,sticky="w",pady=(8,0))
        
        self.start_combo=ttk.Combobox(
            frame,
            textvariable=self.first_player_var,
            values=["human","computer"],
            state="readonly",
            width=16,
        )
        self.start_combo.grid(row=5,column=1,sticky="w",padx=(8,0),pady=(8,0))
        self.update_start_visibility()

    def start_game(self):
        # For testing
        global nodes_generated,nodes_evaluated,move_times
        nodes_generated=0
        nodes_evaluated=0
        move_times=[]
        
        start_number=self.start_var.get()
        self.turn_count=0

        if(start_number<8 or start_number>18):
            messagebox.showerror("Error","The start number should be between 8 and 18.")
            return

        mode=self.mode_var.get()

        if mode=="Player vs Player":
            self.player0_type="human"
            self.player1_type="human"
        elif mode=="Player vs AI":
            self.player0_type="human"
            self.player1_type="ai"
        else:
            self.player0_type="ai"
            self.player1_type="ai"

        start_turn=0 if((self.first_player_var.get())=="human") else 1
        self.state=GameState(n=start_number,score_p0=0,score_p1=0,turn=start_turn)

        self._build_game_screen()
        self.refresh_ui()
        self.after(1500,self.ai_play)





    def _build_game_screen(self):
        self._clear()

        scrn=ttk.Frame(self, padding=12)
        scrn.grid(row=0,column=0)
        
        self.info_label = ttk.Label(scrn,text="",font=("Segoe UI",11,"bold"))
        self.info_label.grid(row=0,column=0,columnspan=3,sticky="w")
        

        self.score_label=ttk.Label(scrn,text="")
        self.score_label.grid(row=1,column=0,columnspan=3,sticky="w",pady=(6,0))
        
        self.turn_label=ttk.Label(scrn,text="")
        self.turn_label.grid(row=2,column=0,columnspan=3,sticky="w",pady=(6,0))
        
        moves=ttk.LabelFrame(scrn,text="Choose a move",padding=10)
        moves.grid(row=3,column=0,columnspan=3,pady=(10,0))

        self.btn2=ttk.Button(moves,text="×2",command=lambda:self.play_move(2),width=8)
        self.btn3=ttk.Button(moves,text="×3",command=lambda:self.play_move(3),width=8)
        self.btn4=ttk.Button(moves,text="×4",command=lambda:self.play_move(4),width=8)

        self.btn2.grid(row=0,column=0,padx=6)
        self.btn3.grid(row=0,column=1,padx=6)
        self.btn4.grid(row=0,column=2,padx=6)

        btm=ttk.Frame(scrn)
        btm.grid(row=4,column=0,columnspan=3,pady=(12,0))

        ttk.Button(btm,text="Restart",command=self._build_start_screen).grid(row=0,column=0,padx=(0,8))
        ttk.Button(btm,text="Leave",command=self.destroy).grid(row=0,column=1)
        

    def current_player_type(self):
        assert self.state is not None
        return self.player0_type if(self.state.turn==0) else self.player1_type



    def refresh_ui(self):
        assert self.state is not None

        turn_name="J0" if(self.state.turn==0) else "J1"

        self.info_label.config(text=f"Current number: {self.state.n}  |  Turn: {turn_name}")
        self.score_label.config(text=f"Scores: J0 = {self.state.score_p0}   |   J1 = {self.state.score_p1}")
        self.turn_label.config(text=f"Turn count: {self.turn_count}")

        ended_game=self.state.is_terminal()
        is_human_turn=(self.current_player_type()=="human")
        enable=(not ended_game) and is_human_turn

        for btn in (self.btn2,self.btn3,self.btn4):
            btn.state(["!disabled"] if enable else ["disabled"])

        if ended_game:
            self.show_result()

    def show_result(self):
        assert self.state is not None
        if self.state.score_p0>self.state.score_p1:
            res="J0 wins !"
        elif self.state.score_p1>self.state.score_p0:
            res="J1 wins !"
        else:
            res="Even."

        messagebox.showinfo("End of the game",f"n={self.state.n}\nJ0={self.state.score_p0} | J1={self.state.score_p1}\n\n{res}")
        
        # For testing
        avg_time=sum(move_times)/len(move_times) if(move_times) else 0
        print("Winner:",res)
        print("Nodes generated:",nodes_generated)
        print("Nodes evaluated:",nodes_evaluated)
        print("Average move time:",avg_time)
        
        
        
    def play_move(self,k):
        assert self.state is not None
        if self.state.is_terminal():
            return

        self.state=self.state.apply_move(k)
        self.turn_count+=1
        self.refresh_ui()
        self.after(1500,self.ai_play)
    
    
    # Does nothing if there is no AI or if it is not AI's turn yet
    def ai_play(self):
        if(self.state is None or self.state.is_terminal()) or (self.current_player_type()!="ai"):
            return

        ai_player=self.state.turn
        depth=int(self.depth_var.get())
        
        start=time.time()
        if self.algo_var.get()=="Minimax":  
            move=best_move_minimax(self.state,depth,ai_player)
        else:
            move=best_move_alphabeta(self.state,depth,ai_player)
            
        end=time.time()
        move_times.append(end-start)
        self.play_move(move)

if __name__=="__main__":
    App().mainloop()





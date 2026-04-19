#!/bin/bash
cd "$(dirname "$0")"

while true; do
  echo ""
  echo "========================================"
  echo "  Git Status"
  echo "========================================"
  git status
  echo ""
  echo "========================================"
  echo "  Recent Commits"
  echo "========================================"
  git log --oneline -10
  echo ""
  echo "========================================"
  echo "  Actions"
  echo "========================================"
  echo "  1) git add <file>    — stage a file"
  echo "  2) git add .         — stage all changes"
  echo "  3) git commit        — commit staged changes"
  echo "  4) git diff          — show unstaged changes"
  echo "  5) git diff --staged — show staged changes"
  echo "  6) git restore <file>— discard changes in file"
  echo "  7) git push          — push to remote"
  echo "  8) git pull          — pull from remote"
  echo "  9) custom command    — type any git command"
  echo "  s) refresh status    — re-show status & log"
  echo "  0) exit"
  echo ""
  read -p "Choose [0-9/s]: " choice

  case "$choice" in
    1)
      read -p "File to stage (e.g. app.py): " f
      git add "$f" && echo "✓ Staged: $f"
      ;;
    2)
      git add .
      echo "✓ All changes staged"
      ;;
    3)
      read -p "Commit message: " msg
      git commit -m "$msg"
      ;;
    4)
      git diff
      ;;
    5)
      git diff --staged
      ;;
    6)
      read -p "File to restore: " f
      read -p "Are you sure you want to discard changes in '$f'? [y/N]: " confirm
      [[ "$confirm" =~ ^[Yy]$ ]] && git restore "$f" && echo "✓ Restored: $f"
      ;;
    7)
      git push
      ;;
    8)
      git pull
      ;;
    9)
      read -p "git " cmd
      git $cmd
      ;;
    s|S)
      continue
      ;;
    0)
      echo "Bye!"
      exit 0
      ;;
    *)
      echo "Invalid choice"
      ;;
  esac

  echo ""
  read -p "Press Enter to continue..."
done

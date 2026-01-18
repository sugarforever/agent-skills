# SRT Format Reference

## File Structure

An SRT (SubRip Subtitle) file consists of sequential subtitle entries, each containing:

```
1
00:00:01,500 --> 00:00:04,500
First line of subtitle text
Optional second line

2
00:00:04,700 --> 00:00:07,666
Next subtitle text

```

## Entry Components

### 1. Sequence Number
- Sequential integer starting from 1
- **Must be preserved exactly**
- No gaps or duplicates allowed

### 2. Timestamp Line
```
HH:MM:SS,mmm --> HH:MM:SS,mmm
```
- Start time --> End time
- Hours:Minutes:Seconds,Milliseconds
- Uses comma (,) as decimal separator, NOT period
- **Must be preserved exactly - NEVER modify**

### 3. Text Content
- One or more lines of text
- This is the ONLY part to correct
- Empty line separates entries

## Critical Rules for Subtitle Correction

### DO
- Correct spelling and terminology errors in text lines
- Maintain all line breaks within subtitle text
- Preserve empty lines between entries
- Keep sequence numbers unchanged
- Keep timestamps unchanged

### DON'T
- Modify timestamp values
- Change sequence numbers
- Merge multiple entries
- Split single entries
- Add or remove entries
- Change the comma in timestamps to period

## Example Correction

### Before (with errors):
```
53
00:02:23,433 --> 00:02:25,833
定义了一款工具summers conversation

54
00:02:26,133 --> 00:02:28,166
这款工具除了用了Lantern
```

### After (corrected):
```
53
00:02:23,433 --> 00:02:25,833
定义了一款工具summarize_conversation

54
00:02:26,133 --> 00:02:28,166
这款工具除了用了LangChain
```

## Processing Large Files

For files with many entries:

1. **Read in chunks** using line ranges
2. **Track position** to ensure complete coverage
3. **Verify entry count** matches after correction
4. **Check continuity** - no missing sequence numbers

## Validation Checklist

Before outputting corrected file:

- [ ] Entry count matches original
- [ ] All sequence numbers present (1 to N)
- [ ] All timestamps unchanged
- [ ] No malformed timestamp lines
- [ ] Empty line between each entry
- [ ] No trailing whitespace issues

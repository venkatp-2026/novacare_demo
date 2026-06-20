"""
INTERVAL PROBLEMS - Interview Practice
=======================================
Common interval manipulation problems with optimal solutions.
"""

from operator import itemgetter

# ============================================================================
# PROBLEM 1: MERGE INTERVALS
# ============================================================================
"""
Problem: Merge Intervals

Given an array of intervals where intervals[i] = [start_i, end_i], 
merge all overlapping intervals and return an array of the non-overlapping 
intervals that cover all the intervals in the input.

Example 1:
Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]
Explanation: Since intervals [1,3] and [2,6] overlap, merge them into [1,6].

Example 2:
Input: intervals = [[1,4],[4,5]]
Output: [[1,5]]
Explanation: Intervals [1,4] and [4,5] are considered overlapping.

Constraints:
- 1 <= intervals.length <= 10^4
- intervals[i].length == 2
- 0 <= start_i <= end_i <= 10^4

Clarifying questions to ask:
1. Are the intervals sorted by start time? (Assume no)
2. Can I modify the input or should I create a new array? (New array preferred)
3. How do we handle edge cases like empty input? (Return empty)
4. Are intervals inclusive on both ends? (Yes)
"""

def merge_intervals(intervals):
    """
    Merge overlapping intervals.
    
    Algorithm:
    1. Sort intervals by start time - O(n log n)
    2. Initialize result with first interval
    3. For each subsequent interval:
       - If it overlaps with the last merged interval, extend the end
       - Otherwise, add it as a new interval
    
    Time Complexity: O(n log n) - dominated by sorting
    Space Complexity: O(n) - for the output array
    """
    if not intervals:
        return []
    
    # Sort by start time using itemgetter (more efficient than lambda)
    intervals.sort(key=itemgetter(0))
    
    merged = [intervals[0]]
    
    for current in intervals[1:]:
        last_merged = merged[-1]
        
        # Check if current interval overlaps with last merged interval
        if current[0] <= last_merged[1]:
            # Merge by extending the end time
            last_merged[1] = max(last_merged[1], current[1])
        else:
            # No overlap, add as new interval
            merged.append(current)
    
    return merged


# Test cases for Merge Intervals
if __name__ == "__main__":
    print("=" * 60)
    print("PROBLEM 1: MERGE INTERVALS")
    print("=" * 60)
    
    test_cases = [
        [[1,3],[2,6],[8,10],[15,18]],
        [[1,4],[4,5]],
        [[1,4],[0,4]],
        [[1,4],[2,3]],
        []
    ]
    
    for i, intervals in enumerate(test_cases, 1):
        result = merge_intervals(intervals.copy())
        print(f"Test {i}: {intervals}")
        print(f"Result: {result}\n")


# ============================================================================
# PROBLEM 2: MINIMUM MEETING ROOMS (Meeting Rooms II)
# ============================================================================
"""
Problem: Minimum Meeting Rooms

Given an array of meeting time intervals where intervals[i] = [start_i, end_i],
determine the minimum number of conference rooms required to schedule all meetings
without conflicts.

Example 1:
Input: intervals = [[0,30],[5,10],[15,20]]
Output: 2
Explanation: One room for [0,30], another for [5,10] and [15,20].

Example 2:
Input: intervals = [[7,10],[2,4]]
Output: 1
Explanation: Only one room needed as meetings don't overlap.

Example 3:
Input: intervals = [[1,5],[2,3],[3,6],[4,7]]
Output: 3
Explanation: At time 4, three meetings overlap.

Constraints:
- 1 <= intervals.length <= 10^4
- 0 <= start_i < end_i <= 10^6

Clarifying questions to ask:
1. Are meetings sorted by start time? (Assume no)
2. Is the end time exclusive or inclusive? (Assume exclusive - meeting ending at 10 frees the room at 10)
3. Can a room be reused immediately? (Yes, if end_i == start_j)
4. What about empty input? (Return 0)
"""

import heapq

def min_meeting_rooms(intervals):
    """
    Find minimum number of meeting rooms required.
    
    Algorithm (Min-Heap approach):
    1. Sort intervals by start time - O(n log n)
    2. Use a min-heap to track end times of ongoing meetings
    3. For each meeting:
       - If earliest-ending meeting has finished, reuse that room (pop heap)
       - Add current meeting's end time to heap
    4. Heap size = number of rooms needed
    
    Time Complexity: O(n log n) - sorting + n heap operations
    Space Complexity: O(n) - heap can contain all meetings in worst case
    """
    if not intervals:
        return 0
    
    # Sort meetings by start time using itemgetter
    intervals.sort(key=itemgetter(0))
    
    # Min-heap to track end times of meetings in progress
    rooms = []
    
    for meeting in intervals:
        start, end = meeting
        
        # If earliest-ending meeting has finished, reuse that room
        if rooms and rooms[0] <= start:
            heapq.heappop(rooms)
        
        # Allocate room for current meeting (either reused or new)
        heapq.heappush(rooms, end)
    
    # Number of rooms = heap size
    return len(rooms)


def min_meeting_rooms_chronological(intervals):
    """
    Alternative approach using chronological ordering (event sweep).
    
    Algorithm:
    1. Create separate arrays for start and end times, sort both
    2. Use two pointers to process events chronologically
    3. When a meeting starts, increment room count
    4. When a meeting ends, decrement room count
    5. Track the maximum room count seen
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if not intervals:
        return 0
    
    starts = sorted([interval[0] for interval in intervals])
    ends = sorted([interval[1] for interval in intervals])
    
    rooms_needed = 0
    max_rooms = 0
    start_ptr = 0
    end_ptr = 0
    
    while start_ptr < len(intervals):
        # Meeting starting
        if starts[start_ptr] < ends[end_ptr]:
            rooms_needed += 1
            max_rooms = max(max_rooms, rooms_needed)
            start_ptr += 1
        else:
            # Meeting ending, room freed
            rooms_needed -= 1
            end_ptr += 1
    
    return max_rooms


# Test cases for Minimum Meeting Rooms
def test_meeting_rooms():
    print("=" * 60)
    print("PROBLEM 2: MINIMUM MEETING ROOMS")
    print("=" * 60)
    
    test_cases = [
        [[0,30],[5,10],[15,20]],
        [[7,10],[2,4]],
        [[1,5],[2,3],[3,6],[4,7]],
        [[1,10],[2,7],[3,19],[8,12],[10,20],[11,30]],
        [[13,15],[1,13]],
        []
    ]
    
    for i, intervals in enumerate(test_cases, 1):
        result_heap = min_meeting_rooms(intervals.copy())
        result_chrono = min_meeting_rooms_chronological(intervals.copy())
        print(f"Test {i}: {intervals}")
        print(f"Min Rooms (Heap): {result_heap}")
        print(f"Min Rooms (Chronological): {result_chrono}")
        print()


if __name__ == "__main__":
    test_meeting_rooms()


# ============================================================================
# PROBLEM 3: INSERT INTERVAL
# ============================================================================
"""
Problem: Insert Interval

You are given an array of non-overlapping intervals sorted by start time,
and a new interval. Insert the new interval into the array and merge if necessary.

Example 1:
Input: intervals = [[1,3],[6,9]], newInterval = [2,5]
Output: [[1,5],[6,9]]

Example 2:
Input: intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval = [4,8]
Output: [[1,2],[3,10],[12,16]]
Explanation: The new interval [4,8] overlaps with [3,5],[6,7],[8,10].

Example 3:
Input: intervals = [], newInterval = [5,7]
Output: [[5,7]]

Constraints:
- 0 <= intervals.length <= 10^4
- intervals[i].length == 2
- intervals is sorted by start_i in ascending order
- newInterval.length == 2
"""

def insert_interval(intervals, new_interval):
    """
    Insert and merge new interval into sorted interval list.
    
    Algorithm:
    1. Add all intervals that end before new interval starts
    2. Merge all overlapping intervals with new interval
    3. Add remaining intervals
    
    Time Complexity: O(n)
    Space Complexity: O(n) for result
    """
    result = []
    i = 0
    n = len(intervals)
    
    # Add all intervals ending before new interval starts
    while i < n and intervals[i][1] < new_interval[0]:
        result.append(intervals[i])
        i += 1
    
    # Merge overlapping intervals
    while i < n and intervals[i][0] <= new_interval[1]:
        new_interval[0] = min(new_interval[0], intervals[i][0])
        new_interval[1] = max(new_interval[1], intervals[i][1])
        i += 1
    result.append(new_interval)
    
    # Add remaining intervals
    while i < n:
        result.append(intervals[i])
        i += 1
    
    return result


def test_insert_interval():
    print("=" * 60)
    print("PROBLEM 3: INSERT INTERVAL")
    print("=" * 60)
    
    test_cases = [
        ([[1,3],[6,9]], [2,5]),
        ([[1,2],[3,5],[6,7],[8,10],[12,16]], [4,8]),
        ([], [5,7]),
        ([[1,5]], [0,0]),
        ([[1,5]], [6,8]),
    ]
    
    for i, (intervals, new_interval) in enumerate(test_cases, 1):
        result = insert_interval(intervals.copy(), new_interval.copy())
        print(f"Test {i}: intervals={intervals}, new={new_interval}")
        print(f"Result: {result}\n")


# ============================================================================
# PROBLEM 4: INTERVAL LIST INTERSECTIONS
# ============================================================================
"""
Problem: Interval List Intersections

You are given two lists of closed intervals, firstList and secondList.
Each list is pairwise disjoint and sorted. Return the intersection of these two lists.

Example 1:
Input: firstList = [[0,2],[5,10],[13,23],[24,25]], 
       secondList = [[1,5],[8,12],[15,24],[25,26]]
Output: [[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]

Example 2:
Input: firstList = [[1,3],[5,9]], secondList = []
Output: []

Constraints:
- 0 <= firstList.length, secondList.length <= 1000
- firstList[i].length == 2
- Both lists are sorted and disjoint
"""

def interval_intersection(firstList, secondList):
    """
    Find all intersections between two interval lists.
    
    Algorithm:
    1. Use two pointers, one for each list
    2. For each pair of intervals, check if they overlap
    3. If overlap exists: intersection = [max(start1, start2), min(end1, end2)]
    4. Move pointer for interval that ends first
    
    Time Complexity: O(m + n)
    Space Complexity: O(min(m, n)) for output
    """
    result = []
    i, j = 0, 0
    
    while i < len(firstList) and j < len(secondList):
        start1, end1 = firstList[i]
        start2, end2 = secondList[j]
        
        # Check if intervals overlap
        # Two intervals [a,b] and [c,d] overlap if max(a,c) <= min(b,d)
        start_intersect = max(start1, start2)
        end_intersect = min(end1, end2)
        
        if start_intersect <= end_intersect:
            result.append([start_intersect, end_intersect])
        
        # Move pointer for interval that ends first
        if end1 < end2:
            i += 1
        else:
            j += 1
    
    return result


def test_interval_intersection():
    print("=" * 60)
    print("PROBLEM 4: INTERVAL LIST INTERSECTIONS")
    print("=" * 60)
    
    test_cases = [
        ([[0,2],[5,10],[13,23],[24,25]], [[1,5],[8,12],[15,24],[25,26]]),
        ([[1,3],[5,9]], []),
        ([[1,7]], [[3,10]]),
    ]
    
    for i, (first, second) in enumerate(test_cases, 1):
        result = interval_intersection(first, second)
        print(f"Test {i}:")
        print(f"  First:  {first}")
        print(f"  Second: {second}")
        print(f"  Result: {result}\n")


# ============================================================================
# PROBLEM 5: NON-OVERLAPPING INTERVALS
# ============================================================================
"""
Problem: Non-overlapping Intervals

Given an array of intervals, find the minimum number of intervals you need 
to remove to make the rest of the intervals non-overlapping.

Example 1:
Input: intervals = [[1,2],[2,3],[3,4],[1,3]]
Output: 1
Explanation: Remove [1,3] and the rest are non-overlapping.

Example 2:
Input: intervals = [[1,2],[1,2],[1,2]]
Output: 2
Explanation: Remove 2 intervals to keep one.

Example 3:
Input: intervals = [[1,2],[2,3]]
Output: 0
Explanation: No need to remove any intervals.

Constraints:
- 1 <= intervals.length <= 10^5
- intervals[i].length == 2
"""

def erase_overlap_intervals(intervals):
    """
    Find minimum number of intervals to remove for non-overlapping set.
    
    Algorithm (Greedy):
    1. Sort intervals by end time
    2. Keep track of the end of the last non-overlapping interval
    3. For each interval:
       - If it starts >= last end, keep it (update last end)
       - Otherwise, it overlaps, so remove it (increment count)
    
    Intuition: Greedy choice - always keep the interval that ends earliest
    to leave maximum room for future intervals.
    
    Time Complexity: O(n log n)
    Space Complexity: O(1)
    """
    if not intervals:
        return 0
    
    # Sort by end time using itemgetter
    intervals.sort(key=itemgetter(1))
    
    removals = 0
    last_end = intervals[0][1]
    
    for i in range(1, len(intervals)):
        start, end = intervals[i]
        
        if start >= last_end:
            # No overlap, keep this interval
            last_end = end
        else:
            # Overlap detected, remove this interval
            removals += 1
    
    return removals


def test_erase_overlap_intervals():
    print("=" * 60)
    print("PROBLEM 5: NON-OVERLAPPING INTERVALS")
    print("=" * 60)
    
    test_cases = [
        [[1,2],[2,3],[3,4],[1,3]],
        [[1,2],[1,2],[1,2]],
        [[1,2],[2,3]],
        [[1,100],[11,22],[1,11],[2,12]],
    ]
    
    for i, intervals in enumerate(test_cases, 1):
        result = erase_overlap_intervals(intervals.copy())
        print(f"Test {i}: {intervals}")
        print(f"Min removals: {result}\n")


# ============================================================================
# RUN ALL TESTS
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("INTERVAL PROBLEMS - COMPLETE TEST SUITE")
    print("="*60 + "\n")
    
    # Problem 1: Merge Intervals
    print("=" * 60)
    print("PROBLEM 1: MERGE INTERVALS")
    print("=" * 60)
    test_cases_1 = [
        [[1,3],[2,6],[8,10],[15,18]],
        [[1,4],[4,5]],
        [[1,4],[0,4]],
        [[1,4],[2,3]],
        []
    ]
    for i, intervals in enumerate(test_cases_1, 1):
        result = merge_intervals(intervals.copy())
        print(f"Test {i}: {intervals}")
        print(f"Result: {result}\n")
    
    # Problem 2: Minimum Meeting Rooms
    test_meeting_rooms()
    
    # Problem 3: Insert Interval
    test_insert_interval()
    
    # Problem 4: Interval Intersections
    test_interval_intersection()
    
    # Problem 5: Non-overlapping Intervals
    test_erase_overlap_intervals()
    
    print("=" * 60)
    print("ALL TESTS COMPLETE!")
    print("=" * 60)


# ============================================================================
# PRODUCTION VERSION: OBJECT-ORIENTED APPROACH WITH DATETIME
# ============================================================================
"""
Real-world production code should use objects with datetime fields instead of lists.
This provides better type safety, validation, and readability.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class TimeInterval:
    """
    Represents a time interval with start and end datetime objects.
    
    Benefits over list-based approach:
    - Type safety: ensures start/end are datetime objects
    - Self-documenting: clear what each field represents
    - Built-in comparison: leverages datetime operators
    - Validation: can enforce start < end
    - Extensible: easy to add metadata (title, location, etc.)
    """
    start_time: datetime
    end_time: datetime
    title: Optional[str] = None
    
    def __post_init__(self):
        """Validate that start_time comes before end_time."""
        if self.start_time >= self.end_time:
            raise ValueError(f"start_time must be before end_time: {self.start_time} >= {self.end_time}")
    
    def __lt__(self, other):
        """Enable sorting by start_time using built-in sort()."""
        return self.start_time < other.start_time
    
    def __repr__(self):
        """Readable string representation."""
        if self.title:
            return f"TimeInterval({self.title}: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
        return f"TimeInterval({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
    
    def overlaps_with(self, other: 'TimeInterval') -> bool:
        """
        Check if this interval overlaps with another.
        Uses datetime comparison operators.
        """
        return self.start_time <= other.end_time and other.start_time <= self.end_time
    
    def merge_with(self, other: 'TimeInterval') -> 'TimeInterval':
        """
        Merge this interval with another overlapping interval.
        Returns a new merged interval.
        """
        if not self.overlaps_with(other):
            raise ValueError(f"Cannot merge non-overlapping intervals: {self} and {other}")
        
        return TimeInterval(
            start_time=min(self.start_time, other.start_time),
            end_time=max(self.end_time, other.end_time),
            title=f"{self.title or 'Merged'} + {other.title or 'Merged'}" if self.title or other.title else None
        )
    
    @property
    def duration(self) -> timedelta:
        """Get the duration of this interval."""
        return self.end_time - self.start_time


def merge_time_intervals(intervals: List[TimeInterval]) -> List[TimeInterval]:
    """
    Merge overlapping TimeInterval objects.
    
    Notice how clean this is:
    - Just call intervals.sort() - no key parameter needed!
    - Use overlaps_with() method instead of manual comparison
    - Use merge_with() method for merging logic
    """
    if not intervals:
        return []
    
    # Sort by start_time - uses __lt__ method, no key needed!
    intervals.sort()
    
    merged = [intervals[0]]
    
    for current in intervals[1:]:
        last_merged = merged[-1]
        
        # Use the overlaps_with method - much more readable!
        if current.overlaps_with(last_merged):
            # Merge intervals
            merged[-1] = last_merged.merge_with(current)
        else:
            # No overlap, add as new interval
            merged.append(current)
    
    return merged


def min_meeting_rooms_objects(intervals: List[TimeInterval]) -> int:
    """
    Find minimum meeting rooms using TimeInterval objects.
    
    Notice: heap operations work directly with datetime objects
    because they have built-in comparison operators!
    """
    if not intervals:
        return 0
    
    # Sort by start_time - just call sort()!
    intervals.sort()
    
    # Min-heap of end times (datetime objects)
    rooms = []
    
    for meeting in intervals:
        # Compare datetime objects directly using <=
        if rooms and rooms[0] <= meeting.start_time:
            heapq.heappop(rooms)
        
        # Push datetime object directly to heap
        heapq.heappush(rooms, meeting.end_time)
    
    return len(rooms)


def find_free_time_slots(busy_intervals: List[TimeInterval], 
                         work_start: datetime, 
                         work_end: datetime,
                         min_duration: timedelta) -> List[TimeInterval]:
    """
    Find all free time slots during working hours.
    
    This is a common real-world problem that's easier with objects!
    """
    if not busy_intervals:
        return [TimeInterval(work_start, work_end, "Free all day")]
    
    # Merge overlapping busy intervals first
    busy_intervals.sort()
    merged_busy = []
    
    for interval in busy_intervals:
        # Only consider intervals during working hours
        if interval.end_time <= work_start or interval.start_time >= work_end:
            continue
        
        # Clip to working hours
        clipped_start = max(interval.start_time, work_start)
        clipped_end = min(interval.end_time, work_end)
        clipped = TimeInterval(clipped_start, clipped_end)
        
        if not merged_busy or not clipped.overlaps_with(merged_busy[-1]):
            merged_busy.append(clipped)
        else:
            merged_busy[-1] = merged_busy[-1].merge_with(clipped)
    
    # Find gaps between busy intervals
    free_slots = []
    
    # Check for free time before first meeting
    if not merged_busy or merged_busy[0].start_time > work_start:
        gap_end = merged_busy[0].start_time if merged_busy else work_end
        gap = TimeInterval(work_start, gap_end, "Morning free slot")
        if gap.duration >= min_duration:
            free_slots.append(gap)
    
    # Check gaps between meetings
    for i in range(len(merged_busy) - 1):
        gap_start = merged_busy[i].end_time
        gap_end = merged_busy[i + 1].start_time
        if gap_end > gap_start:
            gap = TimeInterval(gap_start, gap_end, f"Free slot {i+1}")
            if gap.duration >= min_duration:
                free_slots.append(gap)
    
    # Check for free time after last meeting
    if merged_busy and merged_busy[-1].end_time < work_end:
        gap = TimeInterval(merged_busy[-1].end_time, work_end, "Evening free slot")
        if gap.duration >= min_duration:
            free_slots.append(gap)
    
    return free_slots


# Test the production version
def test_production_version():
    print("\n" + "=" * 60)
    print("PRODUCTION VERSION: OBJECT-ORIENTED WITH DATETIME")
    print("=" * 60 + "\n")
    
    # Create a base date for today
    base_date = datetime(2026, 6, 17, 9, 0)  # 9:00 AM today
    
    print("Example 1: Merge Time Intervals")
    print("-" * 60)
    meetings = [
        TimeInterval(base_date + timedelta(hours=0), base_date + timedelta(hours=1), "Standup"),
        TimeInterval(base_date + timedelta(hours=0, minutes=30), base_date + timedelta(hours=2), "Design Review"),
        TimeInterval(base_date + timedelta(hours=3), base_date + timedelta(hours=4), "Sprint Planning"),
        TimeInterval(base_date + timedelta(hours=6), base_date + timedelta(hours=7), "1-on-1"),
    ]
    
    print("Original meetings:")
    for m in meetings:
        print(f"  {m}")
    
    merged = merge_time_intervals(meetings.copy())
    print(f"\nMerged intervals: {len(merged)} blocks")
    for m in merged:
        print(f"  {m} (duration: {m.duration})")
    
    print("\n" + "=" * 60)
    print("Example 2: Minimum Meeting Rooms")
    print("-" * 60)
    meetings = [
        TimeInterval(base_date + timedelta(hours=0), base_date + timedelta(hours=2), "Team A"),
        TimeInterval(base_date + timedelta(hours=1), base_date + timedelta(hours=3), "Team B"),
        TimeInterval(base_date + timedelta(hours=2, minutes=30), base_date + timedelta(hours=4), "Team C"),
        TimeInterval(base_date + timedelta(hours=3, minutes=30), base_date + timedelta(hours=5), "Team D"),
    ]
    
    print("Meetings:")
    for m in sorted(meetings):
        print(f"  {m}")
    
    rooms_needed = min_meeting_rooms_objects(meetings.copy())
    print(f"\nMinimum rooms needed: {rooms_needed}")
    
    print("\n" + "=" * 60)
    print("Example 3: Find Free Time Slots (Real-world use case)")
    print("-" * 60)
    work_start = datetime(2026, 6, 17, 9, 0)   # 9 AM
    work_end = datetime(2026, 6, 17, 17, 0)     # 5 PM
    
    busy = [
        TimeInterval(base_date + timedelta(hours=0), base_date + timedelta(hours=1), "Standup"),
        TimeInterval(base_date + timedelta(hours=2), base_date + timedelta(hours=3, minutes=30), "Client Call"),
        TimeInterval(base_date + timedelta(hours=5), base_date + timedelta(hours=6), "Team Sync"),
    ]
    
    print(f"Work hours: {work_start.strftime('%I:%M %p')} - {work_end.strftime('%I:%M %p')}")
    print("\nBusy times:")
    for b in busy:
        print(f"  {b}")
    
    min_duration = timedelta(minutes=30)
    free_slots = find_free_time_slots(busy, work_start, work_end, min_duration)
    
    print(f"\nFree slots (min {min_duration.seconds // 60} min):")
    for slot in free_slots:
        print(f"  {slot} - Duration: {slot.duration}")
    
    print("\n" + "=" * 60)
    print("KEY ADVANTAGES OF OBJECT-ORIENTED APPROACH:")
    print("=" * 60)
    print("✓ No ambiguity: interval.start_time vs interval[0]")
    print("✓ Simple sorting: intervals.sort() uses __lt__ automatically")
    print("✓ Built-in validation: enforces start < end in constructor")
    print("✓ Readable comparisons: if meeting1.overlaps_with(meeting2)")
    print("✓ Rich operations: .duration, .merge_with(), etc.")
    print("✓ Datetime power: all datetime operators (<, >, +, -) work!")
    print("✓ Type hints: IDE autocomplete and type checking")
    print("=" * 60)


if __name__ == "__main__":
    test_production_version()

from datetime import datetime, timezone, timedelta
import pytz

def is_close(date1, date2, threshold_days=1):
    """Check if two dates are within threshold_days of each other"""
    return abs((date1 - date2).total_seconds()) <= threshold_days * 86400

def is_anniversary(date1, date2):
    """Check if dates share the same month and day"""
    return date1.month == date2.month and date1.day == date2.day and date1.year != date2.year

def timestamp_to_datetime(timestamp):
    """Convert timestamp to datetime object"""
    try:
        return datetime.fromtimestamp(timestamp, timezone.utc)
    except:
        return None

def twos_complement(value, bits=32):
    """Calculate two's complement of a value"""
    if value & (1 << (bits - 1)):
        value = value - (1 << bits)
    return value

# Define primary dates for F.C. Doty
PRIMARY_DATES = {
    'BIRTH': '1925-10-24',
    'RPI_GRADUATION': '1946-02-22',
    'IBM_START': '1952-04-29',
    'MEMORY_PROGRAM': '1966-03-07',
    'IBM_RETIREMENT': '1987-06-30',
    'DOI_COMM': '1987-06-24',
    'HIGUCHI_COMM': '1987-04-01',
    'PASSING': '2009-10-23',
    'GRUMMAN_REPORT': '1948-06-01',
    'REPORT_REVISION': '1948-12-01',
    'PATENT_FILING': '1984-05-22',
    'PATENT_ISSUE': '1987-03-03',
    'GENESIS_BLOCK': '2009-01-03'
}

# Original dates in hex
HEX_TIMESTAMPS = {
    'BIRTH': -0x531e0bb0,
    'RPI_GRADUATION': -0x2cdfe8b0,
    'IBM_START': -0x213f5400,
    'IBM_RETIREMENT': 0x20e85100,
    'PASSING': 0x4ae12a40,
    'TARGET_VALUE': 0x29158e29,
    'MODULO_RESULT': 0x29148d80,
    'MAGIC_DIFF': 0x100a9,
    'GRUMMAN_REPORT': -0x2899b9c0,
    'REPORT_REVISION': -0x27a86930,
    'MEMORY_PROGRAM': -0x73027b0,
    'PATENT_FILING': 0x1b1032c0,
    'PATENT_ISSUE': 0x204a6350,
    'HIGUCHI_COMM': 0x207108f8,
    'DOI_COMM': 0x20dff79b,
    'GENESIS_BLOCK': 0x495fab29,
    'IBM_DURATION_END': 0x4227a500,
    'ADD_MAGIC_1': -0x72f2707,
    'SUB_MAGIC_1': -0x7312859
}

MAGIC_NUMBER = 0x29158e29
MAX_YEAR = 2013

# Convert hex timestamps to dates, including magic number operations
dates = []
for label, hex_ts in HEX_TIMESTAMPS.items():
    # Original value
    dt = timestamp_to_datetime(hex_ts)
    if dt and dt.year <= MAX_YEAR:
        dates.append((dt, f"{label} (Original) [0x{hex_ts & 0xFFFFFFFF:08x}]"))
    
    # Add magic number
    hex_plus_magic = hex_ts + MAGIC_NUMBER
    dt_plus = timestamp_to_datetime(hex_plus_magic)
    if dt_plus and dt_plus.year <= MAX_YEAR:
        dates.append((dt_plus, f"{label} (+Magic) [0x{hex_plus_magic & 0xFFFFFFFF:08x}]"))
    
    # Subtract magic number
    hex_minus_magic = hex_ts - MAGIC_NUMBER
    dt_minus = timestamp_to_datetime(hex_minus_magic)
    if dt_minus and dt_minus.year <= MAX_YEAR:
        dates.append((dt_minus, f"{label} (-Magic) [0x{hex_minus_magic & 0xFFFFFFFF:08x}]"))
    
    # Two's complement
    hex_complement = twos_complement(hex_ts)
    dt_complement = timestamp_to_datetime(hex_complement)
    if dt_complement and dt_complement.year <= MAX_YEAR and hex_complement != hex_ts:
        dates.append((dt_complement, f"{label} (2's Complement) [0x{hex_complement & 0xFFFFFFFF:08x}]"))

# Sort dates chronologically
dates.sort(key=lambda x: x[0])

# Find clusters of close dates
clusters = []
current_cluster = []

for i in range(len(dates)):
    if not current_cluster:
        current_cluster = [i]
    else:
        if is_close(dates[i][0], dates[current_cluster[-1]][0]):
            current_cluster.append(i)
        else:
            if len(current_cluster) > 1:
                clusters.append(current_cluster)
            current_cluster = [i]

if len(current_cluster) > 1:
    clusters.append(current_cluster)

# Find anniversaries
anniversaries = []
for i in range(len(dates)):
    for j in range(i + 1, len(dates)):
        if is_anniversary(dates[i][0], dates[j][0]):
            anniversaries.append((i, j))

# Generate the timeline
with open('/home/computeruse/ibm/timeline_v5.md', 'w') as f:
    f.write("# F.C. Doty Timeline Analysis\n\n")
    f.write("Frederick Cessna Doty (F.C. Doty)\n")
    f.write("Born: October 24, 1925 - Huntington, Long Island\n")
    f.write("Died: October 23, 2009 - Kingston, NY\n\n")
    f.write("🔵 indicates clustered dates (within 24 hours)\n")
    f.write("🔴 indicates anniversary dates (same month/day, different years)\n")
    f.write("💚 indicates primary biographical dates\n")
    f.write(f"Magic Number: 0x{MAGIC_NUMBER:08x}\n")
    f.write("Cut-off year: 2013\n\n")
    
    current_year = None
    
    for i, (date, label) in enumerate(dates):
        # Check if this index is part of any cluster
        is_clustered = any(i in cluster for cluster in clusters)
        
        # Check if this index is part of any anniversary
        is_anniversary = any(i in (pair[0], pair[1]) for pair in anniversaries)
        
        # Check if this is a primary date
        date_str = date.strftime('%Y-%m-%d')
        is_primary = any(date_str == pdate for pdate in PRIMARY_DATES.values())
        
        # Add year header if it's a new year
        year = date.year
        if year != current_year:
            f.write(f"\n## {year}\n\n")
            current_year = year
        
        # Format the date line
        markers = []
        if is_clustered:
            markers.append("🔵")
        if is_anniversary:
            markers.append("🔴")
        if is_primary and "(Original)" in label:
            markers.append("💚")
        marker = " ".join(markers) if markers else "•"
        
        f.write(f"{marker} {date.strftime('%Y-%m-%d %H:%M:%S UTC')} - {label}\n")
    
    f.write("\n\n## Identified Date Clusters\n\n")
    for cluster in clusters:
        f.write("\n### Cluster\n")
        for idx in cluster:
            date, label = dates[idx]
            f.write(f"- {date.strftime('%Y-%m-%d %H:%M:%S UTC')} - {label}\n")
        f.write("\n")
    
    f.write("\n## Identified Anniversaries\n\n")
    for idx1, idx2 in anniversaries:
        date1, label1 = dates[idx1]
        date2, label2 = dates[idx2]
        f.write(f"### {date1.strftime('%B %d')}\n")
        f.write(f"- {date1.strftime('%Y-%m-%d %H:%M:%S UTC')} - {label1}\n")
        f.write(f"- {date2.strftime('%Y-%m-%d %H:%M:%S UTC')} - {label2}\n\n")
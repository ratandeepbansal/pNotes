"""Usage tracking and analytics."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px

from ..db.metadata import MetadataDB


class UsageTracker:
    """Track and analyze usage patterns."""

    def __init__(self, metadata_db: Optional[MetadataDB] = None):
        """
        Initialize usage tracker.

        Args:
            metadata_db: MetadataDB instance
        """
        self.metadata_db = metadata_db or MetadataDB()

    def get_overview_stats(self) -> Dict:
        """
        Get overall statistics.

        Returns:
            Dictionary with overview stats
        """
        all_notes = self.metadata_db.get_all_notes()
        total_notes = len(all_notes)

        # Collect tags
        all_tags = []
        total_chars = 0

        for note_id, note_data in all_notes:
            # Tags
            tags = note_data.get('tags', '')
            if tags:
                tag_list = tags.split(',') if isinstance(tags, str) else tags
                all_tags.extend([tag.strip() for tag in tag_list if tag.strip()])

            # Content length
            content = note_data.get('content', '')
            total_chars += len(content)

        unique_tags = len(set(all_tags))
        avg_note_length = total_chars / total_notes if total_notes > 0 else 0

        # Notes without tags (orphans)
        orphans = sum(1 for _, data in all_notes if not data.get('tags'))

        return {
            'total_notes': total_notes,
            'unique_tags': unique_tags,
            'avg_note_length': int(avg_note_length),
            'total_words': total_chars // 5,  # Rough estimate
            'orphan_notes': orphans
        }

    def get_tag_distribution(self, top_k: int = 20) -> List[Dict]:
        """
        Get tag distribution with counts.

        Args:
            top_k: Number of top tags

        Returns:
            List of tag dictionaries
        """
        all_notes = self.metadata_db.get_all_notes()
        tag_counter = Counter()

        for note_id, note_data in all_notes:
            tags = note_data.get('tags', '')
            if tags:
                tag_list = tags.split(',') if isinstance(tags, str) else tags
                for tag in tag_list:
                    tag = tag.strip()
                    if tag:
                        tag_counter[tag] += 1

        top_tags = [
            {'tag': tag, 'count': count}
            for tag, count in tag_counter.most_common(top_k)
        ]

        return top_tags

    def get_creation_timeline(self, days: int = 30) -> Dict:
        """
        Get note creation timeline.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with timeline data
        """
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        recent_notes = self.metadata_db.search_by_date_range(start_date=cutoff)

        # Count notes per day
        day_counts = {}
        for note_id in recent_notes:
            note = self.metadata_db.get_note_by_id(note_id)
            if note and note.get('created_at'):
                date_str = datetime.fromtimestamp(note['created_at']).strftime('%Y-%m-%d')
                day_counts[date_str] = day_counts.get(date_str, 0) + 1

        # Fill in missing days with 0
        date_list = []
        count_list = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days - i - 1)
            date_str = date.strftime('%Y-%m-%d')
            date_list.append(date_str)
            count_list.append(day_counts.get(date_str, 0))

        return {
            'dates': date_list,
            'counts': count_list,
            'total_in_period': sum(count_list),
            'avg_per_day': sum(count_list) / days if days > 0 else 0
        }

    def create_tag_chart(self, top_k: int = 15) -> go.Figure:
        """
        Create bar chart of top tags.

        Args:
            top_k: Number of top tags

        Returns:
            Plotly figure
        """
        tag_data = self.get_tag_distribution(top_k)

        if not tag_data:
            # Empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="No tags found",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            return fig

        tags = [item['tag'] for item in tag_data]
        counts = [item['count'] for item in tag_data]

        fig = go.Figure(data=[
            go.Bar(
                x=counts,
                y=tags,
                orientation='h',
                marker_color='#4A90E2'
            )
        ])

        fig.update_layout(
            title='Top Tags by Count',
            xaxis_title='Number of Notes',
            yaxis_title='Tag',
            height=max(400, len(tags) * 25),
            template='plotly_dark'
        )

        return fig

    def create_timeline_chart(self, days: int = 30) -> go.Figure:
        """
        Create timeline chart of note creation.

        Args:
            days: Number of days to show

        Returns:
            Plotly figure
        """
        timeline = self.get_creation_timeline(days)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=timeline['dates'],
            y=timeline['counts'],
            mode='lines+markers',
            name='Notes Created',
            line=dict(color='#50C878', width=2),
            marker=dict(size=6)
        ))

        fig.update_layout(
            title=f'Note Creation - Last {days} Days',
            xaxis_title='Date',
            yaxis_title='Notes Created',
            height=400,
            template='plotly_dark',
            hovermode='x unified'
        )

        return fig

    def get_activity_heatmap_data(self) -> Dict:
        """
        Get data for activity heatmap (day of week, hour).

        Returns:
            Dictionary with heatmap data
        """
        all_notes = self.metadata_db.get_all_notes()

        # Initialize 7x24 grid (day of week x hour)
        activity_grid = [[0 for _ in range(24)] for _ in range(7)]
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        for note_id, note_data in all_notes:
            created = note_data.get('created_at')
            if created:
                dt = datetime.fromtimestamp(created)
                day_of_week = dt.weekday()  # 0=Monday
                hour = dt.hour
                activity_grid[day_of_week][hour] += 1

        return {
            'grid': activity_grid,
            'day_names': day_names,
            'hours': list(range(24))
        }

    def create_activity_heatmap(self) -> go.Figure:
        """
        Create heatmap of note creation activity.

        Returns:
            Plotly figure
        """
        data = self.get_activity_heatmap_data()

        fig = go.Figure(data=go.Heatmap(
            z=data['grid'],
            x=data['hours'],
            y=data['day_names'],
            colorscale='Blues',
            hoverongaps=False
        ))

        fig.update_layout(
            title='Note Creation Activity (Day/Hour)',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            height=400,
            template='plotly_dark'
        )

        return fig

    def find_inactive_notes(self, days: int = 90) -> List[Dict]:
        """
        Find notes not modified recently.

        Args:
            days: Consider notes inactive if not modified in this many days

        Returns:
            List of inactive notes
        """
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        all_notes = self.metadata_db.get_all_notes()

        inactive = []
        for note_id, note_data in all_notes:
            modified = note_data.get('modified_at', 0)
            if modified < cutoff:
                inactive.append({
                    'id': note_id,
                    'title': note_data.get('title', 'Untitled'),
                    'modified_at': datetime.fromtimestamp(modified).strftime('%Y-%m-%d') if modified > 0 else 'Unknown',
                    'days_ago': int((datetime.now().timestamp() - modified) / 86400) if modified > 0 else None
                })

        # Sort by most inactive
        inactive.sort(key=lambda x: x['days_ago'] if x['days_ago'] else 0, reverse=True)

        return inactive

    def get_most_active_notes(self, top_k: int = 10) -> List[Dict]:
        """
        Get notes that were most recently modified.

        Args:
            top_k: Number of notes to return

        Returns:
            List of recently modified notes
        """
        all_notes = self.metadata_db.get_all_notes()

        # Sort by modified time
        sorted_notes = sorted(
            all_notes,
            key=lambda x: x[1].get('modified_at', 0),
            reverse=True
        )[:top_k]

        active_notes = []
        for note_id, note_data in sorted_notes:
            modified = note_data.get('modified_at', 0)
            active_notes.append({
                'id': note_id,
                'title': note_data.get('title', 'Untitled'),
                'tags': note_data.get('tags', ''),
                'modified_at': datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M') if modified > 0 else 'Unknown'
            })

        return active_notes

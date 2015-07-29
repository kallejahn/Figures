__author__ = 'aleaf'

import matplotlib as mpl
import matplotlib.pyplot as plt
import textwrap
'''
try:
    import seaborn as sb
    seaborn = True
except:
    seaborn = False
'''

class ReportFigures(object):

    # figure sizes (based on 6 picas per inch, see USGS Illustration Standards Guide, p 34
    default_aspect = 6 / 8.0 # h/w
    tall_aspect = 7 / 8.0
    singlecolumn_width = 21/6.0
    doublecolumn_width = 42/6.0

    singlecolumn_size = (singlecolumn_width, singlecolumn_width * default_aspect)
    singlecolumn_sizeT = (singlecolumn_width, singlecolumn_width * tall_aspect)
    doublecolumn_size = (doublecolumn_width, doublecolumn_width * default_aspect)
    doublecolumn_sizeT = (doublecolumn_width, doublecolumn_width * tall_aspect)

    # title wraps
    singlecolumn_title_wrap = 50
    doublecolumn_title_wrap = 120

    # month abbreviations
    month = {1: 'Jan.', 2: 'Feb.', 3: 'Mar.', 4: 'Apr.', 5: 'May', 6: 'June',
             7: 'July', 8: 'Aug.', 9: 'Sept.', 10: 'Oct.', 11: 'Nov.', 12: 'Dec.'}

    # fonts
    default_font = 'Univers 57 Condensed'
    title_font = 'Univers 67 Condensed'
    title_size = 9
    legend_font = 'Univers 67 Condensed'
    legend_titlesize = 9
    legend_headingsize = 8
    basemap_credits_font = 'Univers 47 Condensed Light'
    basemap_credits_fontsize = 7
    
    ymin0=False

    # rcParams
    plotstyle = {'font.family': default_font,
                 'font.size' : 8.0,
                 'axes.linewidth': 0.5,
                 'axes.labelsize': 9,
                 'axes.titlesize': 9,
                 "grid.linewidth": 0.5,
                 'xtick.major.width': 0.5,
                 'ytick.major.width': 0.5,
                 'xtick.minor.width': 0.5,
                 'ytick.minor.width': 0.5,
                 'xtick.labelsize': 8,
                 'ytick.labelsize': 8,
                 'xtick.direction': 'in',
                 'ytick.direction': 'in',
                 'xtick.major.pad': 3,
                 'ytick.major.pad': 3,
                 'axes.edgecolor' : 'k',
                 'figure.figsize': doublecolumn_size}

    ymin0 = False

    def __init__(self):

        pass

    def figure_title(self, ax, title, zorder=200, wrap=50,
                     subplot_prefix='',
                     capitalize=True):

        # save the defaults before setting
        old_fontset = mpl.rcParams['mathtext.fontset']
        old_mathtextit = mpl.rcParams['mathtext.it']
        mpl.rcParams['mathtext.fontset'] = 'custom'
        mpl.rcParams['mathtext.it'] = 'Univers 67 Condensed:italic'

        wrap = wrap
        title = "\n".join(textwrap.wrap(title, wrap)) #wrap title
        if capitalize:
            title = title.capitalize()
        '''
        ax.text(.025, 1.025, title,
                horizontalalignment='left',
                verticalalignment='bottom',
                transform=ax.transAxes, zorder=zorder)
        '''
        if len(subplot_prefix) > 0:
            title = '$\it{}$ '.format(subplot_prefix) + title
        # with Univers 47 Condensed as the font.family, changing the weight to 'bold' doesn't work
        # manually specify a different family for the title
        ax.set_title(title, family=self.title_font, zorder=zorder, loc='left')

        # reinstate existing rcParams
        mpl.rcParams['mathtext.fontset'] = old_fontset
        mpl.rcParams['mathtext.it'] = old_mathtextit

    def legend(self, ax, handles, labels, **kwargs):
        '''Make a legend, following guidelines in USGS Illustration Standards, p. 14

        ax : matplotlib.pyplot axis object
        handles : list
            matplotlib.pyplot handles for each plot
        labels : list
            labels for each plot
        kwargs : dict
            keyword arguments to matplotlib.pyplot.legend()
        '''

        lgkwargs = {'title': 'EXPLANATION',
                    'fontsize': self.legend_headingsize,
                    'frameon': False,
                    'loc': 8,
                    'bbox_to_anchor': (0.5, -0.25)}
        lgkwargs.update(kwargs)

        mpl.rcParams['font.family'] = self.title_font


        lg = ax.legend(handles, labels, **lgkwargs)

        plt.setp(lg.get_title(), fontsize=self.legend_titlesize)
        #reset rcParams back to default
        mpl.rcParams['font.family'] = self.default_font
        return lg

    def axes_numbering(self, ax, format_x=False, enforce_integers=False):
        '''
        Implement these requirements from USGS standards, p 16
        * Use commas in numbers greater than 999
        * Label zero without a decimal point
        * Numbers less than 1 should consist of a zero, a decimal point, and the number
        * Numbers greater than or equal to 1 need a decimal point and trailing zero only where significant figures dictate
        '''

        # enforce minimum value of zero on y axis if data is positive
        if self.ymin0 and ax.get_ylim()[0] < 0:
            ax.set_ylim(0, ax.get_ylim()[1])

        # so clunky, but this appears to be the only way to do it
        def number_formatting(axis_limits, enforce_integers):
            if -10 > axis_limits[0] or axis_limits[1] > 10 or enforce_integers:
                fmt = '{:,.0f}'
            elif -10 <= axis_limits[0] < -1 or 1 < axis_limits[1] <= 10:
                fmt = '{:,.1f}'
            elif -1 <= axis_limits[0] < -.1 or .1 < axis_limits[1] <= 1:
                fmt = '{:,.2f}'
            else:
                fmt = '{:,.2e}'
                
            def format_axis(y, pos):
                y = fmt.format(y)
                return y
            return format_axis

        format_axis = number_formatting(ax.get_ylim(), enforce_integers) 
        ax.get_yaxis().set_major_formatter(mpl.ticker.FuncFormatter(format_axis))

        if format_x:
            format_axis = number_formatting(ax.get_xlim(), enforce_integers) 
            ax.get_xaxis().set_major_formatter(mpl.ticker.FuncFormatter(format_axis))
        
        if enforce_integers:
            ax.get_yaxis().set_major_locator(mpl.ticker.MaxNLocator(integer=True))
            if format_x:
                ax.get_xaxis().set_major_locator(mpl.ticker.MaxNLocator(integer=True))
            
        # correct for edge cases of upper ylim == 1, 10
        # and fix zero to have no decimal places
        def fix_decimal(ticks):
            # ticks are a list of strings
            if float(ticks[-1]) == 10:
                ticks[-1] = '10'
            if float(ticks[-1]) == 1:
                ticks[-1] = '1.0'
            for i, v in enumerate(ticks):
                if float(v) == 0:
                    ticks[i] = '0'
            return ticks

        try:
            [float(l._text.replace(u'\u2212', '-')) for l in ax.get_xticklabels()]
            newxlabels = fix_decimal([fmt.format(float(l._text.replace(u'\u2212', '-'))) for l in ax.get_xticklabels()])
            ax.set_xticklabels(newxlabels)
        except:
            pass

        try:
            [float(l._text.replace(u'\u2212', '-')) for l in ax.get_yticklabels()]
            newylabels = fix_decimal([fmt.format(float(l._text.replace(u'\u2212', '-'))) for l in ax.get_yticklabels()])
            ax.set_yticklabels(newylabels)
        except:
            pass

    def basemap_credits(self, ax, text, wrap=50, y_offset=-0.01):
        """Add basemap credits per the Illustration Standards Guide p27
        """
        text = "\n".join(textwrap.wrap(text, wrap)) #wrap title
        ax.text(0.0, y_offset, text, family=self.basemap_credits_font, fontsize=self.basemap_credits_fontsize,
                transform=ax.transAxes, ha='left', va='top')

    def set_style(self, style='default', width='double', height='default'):
        """
        Set dimmensions of figures to standard report sizes

        Not quite sure yet about the cleanest way to implement multiple customizations of the base settings (styles)
        Seaborn's methodology is somewhat complicated, but may be the way to go for multiple figure styles
        (and it also provides the option of viewing the current style settings with the axes_style() command)


        Parameters
        ----------
        width : string
            Sets the figure width to single or double column
            'double' (default) or 'single'
        height : string
            Sets the aspect of the plot to the Matplotlib default (6:8), or a tall aspect (7:8)
            'default' (default) or 'tall'
        """


        if style == 'timeseries':
            self.plotstyle['grid.linewidth'] = 0
            if width == 'single':
                self.plotstyle['xtick.minor.size'] = 0

        if width == 'single' and height != 'tall':
            self.plotstyle['figure.figsize'] = self.singlecolumn_size

        elif height == 'tall' and width == 'double':
            self.plotstyle['figure.figsize'] = self.doublecolumn_sizeT

        elif height == 'tall' and width == 'single':
            self.plotstyle['figure.figsize'] = self.singlecolumn_sizeT

        else:
            pass

        mpl.rcParams.update(self.plotstyle)

        """Set the aesthetic style of the plots.

        This affects things like the color of the axes, whether a grid is
        enabled by default, and other aesthetic elements.

        Parameters
        ----------
        style : dict, None, or one of {darkgrid, whitegrid, dark, white, ticks}
            A dictionary of parameters or the name of a preconfigured set.
        rc : dict, optional
            Parameter mappings to override the values in the preset seaborn
            style dictionaries. This only updates parameters that are
            considered part of the style definition.

        Examples
        --------
        >>> set_style("whitegrid")

        >>> set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8})

        See Also
        --------
        axes_style : return a dict of parameters or use in a ``with`` statement
                     to temporarily set the style.
        set_context : set parameters to scale plot elements
        set_palette : set the default color palette for figures

        """

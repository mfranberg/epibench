import click
import os
import sys
from epibench import commands

class ComplexCLI( click.MultiCommand ):
    def list_commands(self, ctx):
        rv = []
        cmd_dir = os.path.dirname( commands.__file__ )
        for filename in os.listdir( cmd_dir ):
            if filename.startswith( "cmd_" ) and filename.endswith( ".py" ):
                rv.append( filename[ 4:-3 ] )

        rv.sort( )

        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[ 0 ] == 2:
                name = name.encode( "ascii", "replace" )

            mod_name = "epibench.commands.cmd_{0}".format( name )
            mod = __import__( mod_name, None, None, [ "epibench" ] )
        except ImportError:
            return

        return mod.epibench

class CommandWithHelp(click.Command):
    """A Command subclass that adds the help automatically.
    """

    def parse_args(self, ctx, args):
        """Parse arguments sent to this command.
        The code for this method is taken from MultiCommand:
        https://github.com/mitsuhiko/click/blob/master/click/core.py
        It is Copyright (c) 2014 by Armin Ronacher.
        See the license:
        https://github.com/mitsuhiko/click/blob/master/LICENSE
        """
        if not args and not ctx.resilient_parsing:
            click.echo( ctx.get_help( ) )
            ctx.exit( )
        return super( CommandWithHelp, self ).parse_args( ctx, args )

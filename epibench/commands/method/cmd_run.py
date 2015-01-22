import click
import cPickle

from epigen.commands.command import CommandWithHelp

@click.command( "run", cls = CommandWithHelp, short_help = "(internal) runs a given cluster command." )
@click.argument( "obj_dump", type = click.File( "r" ), required = True )
def epibench(obj_dump):
    func = cPickle.load( obj_dump )
    func( )

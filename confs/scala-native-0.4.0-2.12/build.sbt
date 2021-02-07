scalaVersion := "2.12.13"
enablePlugins(ScalaNativePlugin)
import scala.scalanative.build
nativeConfig ~= {
  _.withGC(build.GC.immix)
   .withMode(build.Mode.releaseFull)
   .withLTO(build.LTO.thin)
}

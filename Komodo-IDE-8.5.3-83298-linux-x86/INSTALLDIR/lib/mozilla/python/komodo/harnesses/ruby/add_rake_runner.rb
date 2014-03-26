begin
require 'rake'
require 'rake/testtask'
rescue LoadError
  require 'rubygems'
  gem 'rake'
  require 'rake/testtask'
end

class Rake::TestTask
  alias old_initialize initialize

  def initialize(*args, &block)
    old_initialize(*args) do |t|
      t.ruby_opts << %Q(-I"#{File.dirname(__FILE__)}" -rload_komodo_runner)
      block.call(t) if block
    end
  end
end
